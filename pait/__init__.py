import inspect
from functools import wraps

from starlette.responses import JSONResponse,UJSONResponse


def params_verify():
    """装饰器"""
    def wrapper(func):
        @wraps(func)
        async def request_param(request, *args, **kwargs):
            # 获取参数
            if request.method == 'GET':
                param_dict = dict(request.query_params)
            else:
                param_dict = await request.json()
            sig = inspect.signature(func)
            param = {
                key: sig.parameters[key]
                for key in sig.parameters
                if sig.parameters[key].annotation != sig.empty
            }
            return_param = sig.return_annotation
            try:
                func_args = []
                for model in param.values():
                    model = model.annotation(**param_dict)
                    func_args.append(model)
                # 处理响应
                response = await func(request, *func_args, **kwargs)
                if type(response) != return_param:
                    raise ValueError(f'response type != {return_param}')
                if dict == return_param:
                    return JSONResponse(response)
                raise TypeError(f'{type(response)} not support')
            except Exception as e:
                # 这里为了示范,把错误抛出来,这里改为e.json,错误信息会更详细的
                return JSONResponse({'error': str(e)})
        return request_param
    return wrapper