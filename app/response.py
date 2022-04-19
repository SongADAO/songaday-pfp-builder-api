import ast
from typing import Any, Dict, Union


def rest_error(
    error: Union[str, Dict[Any, Any]]
) -> Dict[str, Union[bool, Dict[str, Union[int, str]]]]:
    errorCode: Union[int, str] = 0
    errorMessage: str = str(error)

    try:
        error = ast.literal_eval(errorMessage)
    except Exception:
        pass

    is_dict = type(error) is dict

    if is_dict and ("code" in error):
        errorCode: Union[int, str] = error["code"]

    if is_dict and ("message" in error):
        errorMessage: str = error["message"]

    return {
        "success": False,
        "error": {"code": errorCode, "message": errorMessage},
    }


def rest_success():
    return {"success": True}
