import matplotlib
matplotlib.use('Agg') # Headless mode for server deployment

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from env_bescom import BESCOM_EV_Env
import numpy as np

app = FastAPI(title="BESCOM EV Grid Oracle - OpenEnv API")

# Global environment instance
env = BESCOM_EV_Env()

class StepRequest(BaseModel):
    action: int

@app.get("/")
def read_root():
    return {"message": "BESCOM EV Grid Oracle API is online. Use /reset or /step endpoints."}

@app.post("/reset")
def reset_env():
    obs, info = env.reset()
    return {"observation": obs, "info": info}

@app.post("/step")
def step_env(request: StepRequest):
    try:
        obs, reward, terminated, truncated, info = env.step(request.action)
        return {
            "observation": obs,
            "reward": reward,
            "terminated": terminated,
            "truncated": truncated,
            "info": info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
