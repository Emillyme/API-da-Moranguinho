from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Union, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Configuração do banco de dados SQLite
DATABASE_URL = "sqlite:///./moranguinho.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Definindo o modelo do banco de dados
class Personagem(Base):
    __tablename__ = "personagens"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    genero = Column(String)
    fruta_fav = Column(String)
    cor_fav = Column(JSON)  # Usando JSON para permitir listas
    profissao = Column(String)
    personalidade = Column(Text)
    animal_estimacao = Column(JSON)
    imagem = Column(String)


# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicialização da aplicação FastAPI
app = FastAPI(title="Moranguinho API", version="0.0.1")


# Modelos Pydantic
class Moranguinho(BaseModel):
    nome: str
    genero: str
    fruta_fav: str
    cor_fav: Union[str, List[str]]
    profissao: str
    personalidade: str
    animal_estimacao: Union[str, List[str]]
    imagem: str


class MoranguinhoResponse(Moranguinho):
    id: int


# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CRUD Operations
@app.get("/personagens", response_model=List[MoranguinhoResponse])
async def get_todos_personagens(db: Session = Depends(get_db)):
    return db.query(Personagem).all()


@app.get("/personagens/{id_personagem}", response_model=MoranguinhoResponse)
async def get_personagem(id_personagem: int, db: Session = Depends(get_db)):
    personagem = db.query(Personagem).filter(Personagem.id == id_personagem).first()
    if not personagem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Personagem não encontrado')
    return personagem


@app.post("/personagens", response_model=MoranguinhoResponse, status_code=status.HTTP_201_CREATED)
async def criar_personagem(personagem: Moranguinho, db: Session = Depends(get_db)):
    novo_personagem = Personagem(**personagem.dict())
    db.add(novo_personagem)
    db.commit()
    db.refresh(novo_personagem)
    return novo_personagem


@app.put("/personagens/{id_personagem}", response_model=MoranguinhoResponse)
async def atualizar_personagem(id_personagem: int, personagem_atualizado: Moranguinho, db: Session = Depends(get_db)):
    personagem = db.query(Personagem).filter(Personagem.id == id_personagem).first()
    if not personagem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Personagem não encontrado')
    for key, value in personagem_atualizado.dict().items():
        setattr(personagem, key, value)
    db.commit()
    db.refresh(personagem)
    return personagem


@app.patch("/personagens/{id_personagem}", response_model=MoranguinhoResponse)
async def atualizar_parcial_personagem(id_personagem: int, dados_parciais: Moranguinho, db: Session = Depends(get_db)):
    personagem = db.query(Personagem).filter(Personagem.id == id_personagem).first()
    if not personagem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Personagem não encontrado')

    for key, value in dados_parciais.dict(exclude_unset=True).items():
        setattr(personagem, key, value)
    db.commit()
    db.refresh(personagem)
    return personagem


@app.delete("/personagens/{id_personagem}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_personagem(id_personagem: int, db: Session = Depends(get_db)):
    personagem = db.query(Personagem).filter(Personagem.id == id_personagem).first()
    if not personagem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Personagem não encontrado')
    db.delete(personagem)
    db.commit()
    return


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info", reload=True)
