from typing import Dict, Any
from fastapi.openapi.utils import get_openapi

def openapi(self) -> Dict[str, Any]:
    if not self.openapi_schema:

        self.openapi_schema = get_openapi(
            title=self.title,
            version=self.version,
            openapi_version=self.openapi_version,
            description=self.description,
            terms_of_service=self.terms_of_service,
            contact=self.contact,
            license_info=self.license_info,
            routes=self.routes,
            tags=self.openapi_tags,
            servers=self.servers,
        )

    return self.openapi_schema
