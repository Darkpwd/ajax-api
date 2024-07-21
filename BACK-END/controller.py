from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Pessoa
from pydantic import BaseModel
import uvicorn

# Configuração do banco de dados
DATABASE_URL = "sqlite:///sqlite.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)  # Cria as tabelas no banco de dados

app = FastAPI()

# Configuração do CORS
origins = [
    "http://127.0.0.1:5500",  # URL do frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definição do modelo de dados
class Usuario(BaseModel):
    user: str
    email: str
    senha: str

# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para cadastro
@app.post("/cadastro")
def cadastro(usuario: Usuario, db: Session = Depends(get_db)):
    if len(usuario.senha) < 6:
        return {'erro': 1, 'mensagem': 'A senha deve ter pelo menos 6 caracteres'}

    existing_user = db.query(Pessoa).filter_by(email=usuario.email).first()

    if existing_user:
        return {'erro': 2, 'mensagem': 'Email já cadastrado'}

    try:
        novo_usuario = Pessoa(
            usuario=usuario.user,
            email=usuario.email,
            senha=usuario.senha
        )
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)  # Atualiza a instância com os dados do banco
        return {'erro': 0, 'mensagem': 'Usuário cadastrado com sucesso'}
    except Exception as e:
        db.rollback()
        return {'erro': 3, 'mensagem': f'Erro ao cadastrar usuário: {str(e)}'}

# Executar o aplicativo
if __name__ == "__main__":
    uvicorn.run("controller:app", host="0.0.0.0", port=5501, reload=True)
