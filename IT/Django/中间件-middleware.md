# Django-middleware分析

## 一、middleware加载过程-源码分析

django/core/handlers/wsgi.py， line 122:

```python
class WSGIHandler(base.BaseHandler):
    request_class = WSGIRequest

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_middleware()
```

追蹤load_middleware, 在django/core/handlers/base.py, line 23, class BaseHandler:

```python
class BaseHandler:
    ...
    def load_middleware(self):
        """
        Populate middleware lists from settings.MIDDLEWARE.

        Must be called after the environment is fixed (see __call__ in subclasses).
        """
        self._view_middleware = []
        self._template_response_middleware = []
        self._exception_middleware = []

        # 函数定义可以参考下文
        # 忽略异常情况，此处可以简单的看作：handler=self._get_response
        handler = convert_exception_to_response(self._get_response)
        
        # note: 此处以倒序处理MIDDREWARE
        for middleware_path in reversed(settings.MIDDLEWARE):
            # 导入middleware
            middleware = import_string(middleware_path)
            try:
                # 参考下文贴出的MiddlewareMixin源码
                # 实例化一个MiddlewareMixin对象, 该对象的get_response属性设置为handler
                mw_instance = middleware(handler)
            except MiddlewareNotUsed as exc:
                if settings.DEBUG:
                    if str(exc):
                        logger.debug('MiddlewareNotUsed(%r): %s', middleware_path, exc)
                    else:
                        logger.debug('MiddlewareNotUsed: %r', middleware_path)
                continue

            if mw_instance is None:
                raise ImproperlyConfigured(
                    'Middleware factory %s returned None.' % middleware_path
                )

            if hasattr(mw_instance, 'process_view'):
                self._view_middleware.insert(0, mw_instance.process_view)
            if hasattr(mw_instance, 'process_template_response'):
                self._template_response_middleware.append(mw_instance.process_template_response)
            if hasattr(mw_instance, 'process_exception'):
                self._exception_middleware.append(mw_instance.process_exception)

           	# handler更新为一个MiddlewareMixin对象
            # 以函数形式调用该对象（例mw_instance(request)）的时候，实际调用了mw_instance.__call__方法
            handler = convert_exception_to_response(mw_instance)

        # We only assign to this when initialization is complete as it is used
        # as a flag for initialization being complete.
        self._middleware_chain = handler
```

convert_exception_to_response的声明在django/core/handlers/exception.py, line 18, 可以看到该函数实际是封装了异常处理:

```python
def convert_exception_to_response(get_response):
    """
    Wrap the given get_response callable in exception-to-response conversion.

    All exceptions will be converted. All known 4xx exceptions (Http404,
    PermissionDenied, MultiPartParserError, SuspiciousOperation) will be
    converted to the appropriate response, and all other exceptions will be
    converted to 500 responses.

    This decorator is automatically applied to all middleware to ensure that
    no middleware leaks an exception and that the next middleware in the stack
    can rely on getting a response instead of an exception.
    """
    @wraps(get_response)
    def inner(request):
        try:
            response = get_response(request)
        except Exception as exc:
            response = response_for_exception(request, exc)
        return response
    return inner
```

django中的middleware会从一个MiddlewareMixin继承，关于MiddlewareMixin的定义在django/utils/deprecation.py, line 85:

```python
class MiddlewareMixin:
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        response = response or self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response
```

## 二、middleware加载过程-代码运行分析

假设定义setting.MIDDLEWARE定义为[A, B, C]，那么上面过程可以描述为：

```python
handler = wrapped(self._get_response)  # BaseHandler._get_response
for M in [C, B, A]:
    import A
    m_instance = M(handler) # m_instance.get_response = handler
    handler = wrapped(m_instance) # m_instance.__call__
    
self._middleware_chain = handler # A.__call__
```

运行后的结果为：

**note: 为简化分析过程，此处忽略了异常情况**

**实际需考虑convert_exception_to_response，完整的A.get_response应该为convert_exception_to_response(B.__call__)**

```python
C.get_response = BaseHandler._get_response
B.get_response = C.__call__
A.get_response = B.__call__
self._middleware_chain = A.__call__
```

## 三、request处理过程-源码分析

django/core/handlers/wsgi.py, line 133, class WSGIHandler:

```python
class WSGIHandler(base.BaseHandler):
    request_class = WSGIRequest

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_middleware()

    def __call__(self, environ, start_response):
        set_script_prefix(get_script_name(environ))
        signals.request_started.send(sender=self.__class__, environ=environ)
        request = self.request_class(environ)
        
        # 获取response
        response = self.get_response(request)

        response._handler_class = self.__class__

        status = '%d %s' % (response.status_code, response.reason_phrase)
        response_headers = [
            *response.items(),
            *(('Set-Cookie', c.output(header='')) for c in response.cookies.values()),
        ]
        start_response(status, response_headers)
        if getattr(response, 'file_to_stream', None) is not None and environ.get('wsgi.file_wrapper'):
            # If `wsgi.file_wrapper` is used the WSGI server does not call
            # .close on the response, but on the file wrapper. Patch it to use
            # response.close instead which takes care of closing all files.
            response.file_to_stream.close = response.close
            response = environ['wsgi.file_wrapper'](response.file_to_stream, response.block_size)
        return response
```

追蹤, 在django/core/handlers/base.py, line 71, class BaseHandler:

```python
def get_response(self, request):
        """Return an HttpResponse object for the given HttpRequest."""
        # Setup default url resolver for this thread
        set_urlconf(settings.ROOT_URLCONF)
        
        # middleware依次处理
        response = self._middleware_chain(request)
        response._resource_closers.append(request.close)
        if response.status_code >= 400:
            log_response(
                '%s: %s', response.reason_phrase, request.path,
                response=response,
                request=request,
            )
        return response
```

参考上文【middleware加载过程-代码运行分析】的例子，middleware处理过程可看作：

```python
A.__call__(request):
    response = None
    if hasattr(self, 'process_request'):
        response = self.process_request(request)
    # 替换
    response = response or self.get_response(request)
    if hasattr(self, 'process_response'):
        response = self.process_response(request, response)
        return response
```

结合上文MiddlewareMixin.__call__的源码，此处实际是链式调用，依次调用

A.__call__ -> B.__call__ -> C.__call__ -> BaseHandler._get_response，即：

A.process_request --> B.process_request --> C.process_request --> BaseHandler._get_response --> BaseHandler._process_response -- > C.process_response --> B.process_response --> A.process_response

贴一下BaseHandler._get_response的源码:

```python
	def _get_response(self, request):
        """
        Resolve and call the view, then apply view, exception, and
        template_response middleware. This method is everything that happens
        inside the request/response middleware.
        """
        response = None

        if hasattr(request, 'urlconf'):
            urlconf = request.urlconf
            set_urlconf(urlconf)
            resolver = get_resolver(urlconf)
        else:
            resolver = get_resolver()

        resolver_match = resolver.resolve(request.path_info)
        callback, callback_args, callback_kwargs = resolver_match
        request.resolver_match = resolver_match

        # Apply view middleware
        for middleware_method in self._view_middleware:
            response = middleware_method(request, callback, callback_args, callback_kwargs)
            if response:
                break

        if response is None:
            wrapped_callback = self.make_view_atomic(callback)
            try:
                response = wrapped_callback(request, *callback_args, **callback_kwargs)
            except Exception as e:
                response = self.process_exception_by_middleware(e, request)

        # Complain if the view returned None (a common error).
        if response is None:
            if isinstance(callback, types.FunctionType):    # FBV
                view_name = callback.__name__
            else:                                           # CBV
                view_name = callback.__class__.__name__ + '.__call__'

            raise ValueError(
                "The view %s.%s didn't return an HttpResponse object. It "
                "returned None instead." % (callback.__module__, view_name)
            )

        # If the response supports deferred rendering, apply template
        # response middleware and then render the response
        elif hasattr(response, 'render') and callable(response.render):
            for middleware_method in self._template_response_middleware:
                response = middleware_method(request, response)
                # Complain if the template response middleware returned None (a common error).
                if response is None:
                    raise ValueError(
                        "%s.process_template_response didn't return an "
                        "HttpResponse object. It returned None instead."
                        % (middleware_method.__self__.__class__.__name__)
                    )

            try:
                response = response.render()
            except Exception as e:
                response = self.process_exception_by_middleware(e, request)

        return response
```

可以看到url解析即在此处完成，此外还有视图和渲染等功能也在此处调用。

# 参考

[参考一: Django中间件详解](https://blog.csdn.net/Fe_cow/article/details/91344472)

[参考二: Django中间件](https://www.runoob.com/django/django-middleware.html)

[参考三: 自定义Django中间件](https://www.cnblogs.com/276815076/p/9593419.html)