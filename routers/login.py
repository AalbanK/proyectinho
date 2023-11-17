from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/login")
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def process_login(request: Request):
    # Aquí puedes agregar lógica para procesar los datos del formulario
    form_data = await request.form()
    username = form_data["username"]
    password = form_data["password"]
    # Realiza la autenticación y redirige o muestra un mensaje de éxito o error
    # ...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
