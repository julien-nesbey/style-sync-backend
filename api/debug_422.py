from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    try:
        if "multipart/form-data" in request.headers.get("content-type", ""):
            # We don't want to print the whole image payload, just the forms and headers
            form = await request.form()
            print("FORM DATA RECEIVED:", form.keys())
    except:
        pass
    print("422 VALIDATION ERROR DETAILS:")
    print("Errors:", exc.errors())
    print("Headers:", request.headers)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": str(exc.body)},
    )
