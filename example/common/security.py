from typing import TYPE_CHECKING, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

from pait.field import Depends

if TYPE_CHECKING:
    from pait.app.base.security.oauth2 import BaseOAuth2PasswordBearerProxy


class User(BaseModel):
    uid: str = Field(..., description="user id")
    name: str = Field(..., description="user name")
    age: int = Field(..., description="user age")
    sex: str = Field(..., description="user sex")
    scopes: List[str] = Field(..., description="user scopes")


temp_token_dict: Dict[str, User] = {}


def get_current_user(oauth2_pb: "BaseOAuth2PasswordBearerProxy") -> Callable[[str], User]:
    def _check_scope(token: str = Depends.i(oauth2_pb)) -> User:
        user_model: Optional[User] = temp_token_dict.get(token, None)
        if not user_model:
            raise oauth2_pb.security.not_authenticated_exc
        if not oauth2_pb.is_allow(user_model.scopes):
            raise oauth2_pb.security.not_authenticated_exc
        return user_model

    return _check_scope
