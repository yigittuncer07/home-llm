# Home LLM

Deploy your own LLM chat website from home!  

I built this website to have a standard LLM chat interface (like [https://claude.ai](https://claude.ai), [https://gemini.google.com/](https://gemini.google.com/), or any other LLM provider) for my vLLM and llama.cpp instances I have at home, and for the free API keys I have sitting around.  

I host my own instance at [llm.yigittuncer.net](https://llm.yigittuncer.net) if you want to check it out, you can log in with:  

Username: demo@demouser.gmail.com  
Password: password  
This user probably won't have any credits though.  

## Quick Start  

### 1. Prerequisites  

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine installed.  
* *(Optional)* NVIDIA Drivers and [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) if you will launch the vLLM or llama.cpp instance on the same machine as the website, which is how I do it.  

### 2. Configuration  

Clone the repository and set up your environment variables:  

```bash  
git clone https://github.com/yigittuncer07/home-llm  
cd home-llm  
cp .env.example .env  
cp app/frontend/.env.example app/frontend/.env  
  
```  
   
Open `.env` in a text editor and fill in your details if there are any you want to change, especially check the ADMIN info.  

Configure your available models by editing `app/backend/models.yaml` if you want to change the default qwen model.  
**Note:** The docker compose setup is designed to run only a **single local model** at a time (you choose between vLLM or llama.cpp). However, you can mix and match this local model with as many external APIs as you want! You can easily have your local Qwen model running right alongside the Gemini API or OpenAI API just by adding them all to your `models.yaml`.  

### 3. Deployment  

**Option A: Deploy without a local model (APIs only)**  
If you are using remote APIs (like Gemini/OpenAI) or if your local model is running on another machine, run like this to run without spinning up a heavy local model container:  

```bash
docker compose up -d  

```

**Option B: Deploy with vLLM**  
If you want to host an open-source model directly on this machine using your GPU, activate the `vllm` profile. Be sure to set the `backend/models.yaml` file to have the model you want, along with variables in your `.env` file. The default model is Qwen3.5-0.8B.

```bash
docker compose --profile vllm up -d  

```

**Option C: Deploy with llama.cpp (Recommended for GGUF)**  
If you plan to use `.gguf` files (which are highly recommended for home hardware because they run great), activate the `llamacpp` profile instead.  

For this option, you need to set these two specific variables in your `.env` file instead of `LLM_MODEL`:  

* `LLM_HF_REPO`: The Hugging Face repository (e.g., `unsloth/Qwen3.5-0.8B-GGUF`)  
* `LLM_HF_FILE`: The exact file name (e.g., `Qwen3.5-0.8B-Q4_K_M.gguf`)  

When you launch it, llama.cpp will automatically download the model file for you.  
*Note on caching:* The docker-compose file mounts your host machine's `~/.cache/huggingface` directory directly into the container. This means any models you download will be saved safely on your host machine, and you won't have to re-download them if you destroy the docker container!  

```bash 
docker compose --profile llamacpp up -d  
 
```  

### 4. First Steps  

1. Navigate to **http://localhost** in your web browser.  
2. Log in using the `ADMIN_EMAIL` and `ADMIN_PASSWORD` you set in the `.env` file.  
3. Access the **Admin Dashboard** via the user menu.  
4. From the dashboard, you can:  
* Create new user accounts.  
* Manage token limits and model access for individual users.  