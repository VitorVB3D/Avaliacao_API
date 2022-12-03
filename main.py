from fastapi import FastAPI,status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class Pessoa(BaseModel):
    nome: str
    tipoAtendimento: str
    posicao: int
    dataEntrada: datetime
    atendido: bool
    
class PessoaPost(BaseModel):
    nome: str
    tipoAtendimento: str
    
class PessoaGet(BaseModel):
    posicao: int
    tipoAtendimento: str
    nome: str
    dataChegada: datetime
    atendido: bool
    
fila = []

@app.get("/fila")
def Get_Fila():
    filaaux = []
    for item in fila:
        if item.atendido == False:
            schemaPessoaGet = PessoaGet(
                posicao=item.posicao,
                tipoAtendimento=item.tipoAtendimento,
                nome=item.nome,
                dataChegada=item.dataEntrada,
                atendido=item.atendido
            )
            filaaux.append(schemaPessoaGet)
    return filaaux

@app.get("/fila/{id}")
def Get_id_Fila(id: int):
    for item in fila:
        if item.posicao == id:
            schemaPessoaGet = PessoaGet(
                posicao=item.posicao,
                tipoAtendimento=item.tipoAtendimento,
                nome=item.nome,
                dataChegada=item.dataEntrada
            )
            return schemaPessoaGet
    #So vai cair aqui se não achar o ID
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=f"Posição {id} Não se encontra na fila"
    )


def ProximaPosicao(preferencial: str):
    filaPref = []
    filaNom = []
    
    for item in fila:
        if item.posicao > 0:
            if item.tipoAtendimento == "P":
                itemAux = Pessoa(
                    nome = item.nome,
                    tipoAtendimento=item.tipoAtendimento,
                    posicao=filaPref[len(filaPref)-1].posicao + 1 if len(filaPref) > 0 else 1,
                    dataEntrada=item.dataEntrada,
                    atendido=False
                ) 
                filaPref.append(itemAux)
            else:
                itemAux = Pessoa(
                    nome = item.nome,
                    tipoAtendimento=item.tipoAtendimento,
                    posicao=filaNom[len(filaNom)-1].posicao + 1 if len(filaNom) > 0 else 1,
                    dataEntrada=item.dataEntrada,
                    atendido=False
                ) 
                filaNom.append(itemAux)

    if preferencial == 'P':
        for item in fila:
            if item.posicao > 0 and item.tipoAtendimento == 'N':
                item.posicao = item.posicao + 1
                
        return len(filaPref)+1
    else:
        return len(fila)+1

@app.post("/fila")
def Post_Fila(pessoa: PessoaPost):
    if pessoa.tipoAtendimento != 'N' and pessoa.tipoAtendimento != 'P':
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='TipoAtendimento só pode ser N (Normal) ou P (Prioritario)'
        )
    if len(pessoa.nome) > 20:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content='Nome da pessoa deve ter no maximo 20 Caracteres'
        )
    
    schemaPessoa = Pessoa(
        nome = pessoa.nome,
        tipoAtendimento=pessoa.tipoAtendimento,
        posicao=ProximaPosicao(pessoa.tipoAtendimento) if len(fila) > 0 else 1,
        dataEntrada=datetime.now(),
        atendido=False
    )
    fila.append(schemaPessoa)
    fila.sort(key=lambda x: x.posicao)
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content='Pessoa Adicionado na fila com sucesso'
        )

@app.put("/fila")
def put_fila():
    for item in fila:
        item.posicao = item.posicao - 1
        if item.posicao <= 0:
            item.atendido = True
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content= "Atendido com sucesso"  
    )

@app.delete("/fila/{id}")
def delete_Fila(id: int):
    index = 0
    achou = False
    for item in fila:
        if item.posicao == id:
            achou = True
            index = fila.index(item)
            next
        if item.posicao > id:
            item.posicao = item.posicao -1
        
    if achou:
        fila.remove(fila[index])
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f"Posição {id} Removido da fila"
        )  
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=f"Posição {id} Não achado na fila"
    )
    