from fastapi import FastAPI, Body, Depends, HTTPException
import json
from app.model import UserLoginSchema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT

app = FastAPI()

with open("account.json", "r") as read_file:
    data = json.load(read_file)
with open("tryout.json", "r") as read_file:
    datatryout = json.load(read_file)

@app.get('/')
def root():
    return{'Menu':'Item'}

def check_user(user: str, password: str):
    for account in data['account']:
        if user == account['user'] and password == account['password']:
            return True
    return False

@app.post("/user/login", tags=["user"])
async def user_login(user: str, password: str):
    if check_user(user, password):
        return signJWT(user)
    return {
        "error": "Wrong login details!"
    }

@app.post("/user/signup", tags=["user"])
async def user_signup(user: str, email:str, password: str):
    if check_user(user, password):
        return {
            "error": "Account sudah terdaftar!"
        }
    else:
        id=1
        if(len(data['account'])>0):
            id=data['account'][len(data['account'])-1]['id']+1
        new_data={'id': id,'user': user,'email' : email, 'password': password}
        data['account'].append(dict(new_data))
        read_file.close()
        with open("account.json", "w") as write_file:
            json.dump(data,write_file,indent=4)
        write_file.close()
        return {"message": "SignUp Berhasil"}
    raise HTTPException(
        status_code=500, detail=f'Internal Server Error'
    )

@app.get("/menu/all_tryout", dependencies=[Depends(JWTBearer())], tags=["menu"])
async def read_all_tryout():
    return datatryout

@app.get("/menu/tryout", dependencies=[Depends(JWTBearer())], tags=["menu"])
async def read_tryout(idtryout : int):
    for list_tryout in datatryout["tryout"]:
        if list_tryout["id_tryout"] == idtryout:
            return list_tryout
    raise HTTPException(
        status_code = 404, detail =f'Tryout not Found'
    )

@app.put("/menu/saldo", dependencies=[Depends(JWTBearer())], tags=["menu"])
async def isi_saldo(user: str, saldo: int):
    for account in data['account']:
        if account['user'] == user:
            account['saldo'] = account['saldo'] + saldo
            read_file.close()
            with open("account.json", "w") as write_file:
                json.dump(data,write_file,indent=4)
            write_file.close()
            return {"message":"Isi Saldo Berhasil"}
    raise HTTPException(
        status_code=404, detail=f'Item not found'
        )

@app.get("/menu/ceksaldo", dependencies=[Depends(JWTBearer())], tags=["menu"])
async def cek_saldo(user: str):
    for account in data['account']:
        if account['user'] == user:
            return account['saldo']
    return {"error" : "User Tidak Terdaftar"}

@app.delete("/menu/readsaldo", dependencies=[Depends(JWTBearer())], tags=["menu"])
async def read_saldo(item_id: int):
    return data