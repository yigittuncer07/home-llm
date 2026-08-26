# Home LLM

Deploy your own LLM chat website from home!   

I built this website to have a standard LLM chat interface (like https://claude.ai, https://gemini.google.com/, or any other LLM provider) for my VLLM instances I have at home, and for the free API key's I have sitting around.  

I host my own instance at [llm.yigittuncer.net](https://llm.yigittuncer.net) if you want to check it out, you can log in with:  
Username: demo@demouser.gmail.com  
Password: password  
This user probably won't have any credits though.

<img width="1866" height="915" alt="image" src="https://github.com/user-attachments/assets/ca2a80c5-1471-4054-acad-9c9169c2097d" />

 
## Quick Start

### 1. Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine installed.
* *(Optional)* NVIDIA Drivers and [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) if you will launch the VLLM instance on the same machine as the website, which is how I do it.

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

### 3. Deployment

**Option A: Deploy without VLLM**
If you are using remote API's or if VLLM is running on another machine, run like this to run without VLLM:

```bash
docker compose up -d

```

**Option B: Deploy with VLLM**
If you want to host an open-source model directly on this machine using your GPU, activate the `vllm` profile. Be sure to set the backend/models.yaml file to have the model you want, along with variables in your .env file. The default model is Qwen3.5-0.8B.
*
```bash
docker compose --profile vllm up -d

```

### 4. First Steps

1. Navigate to **http://localhost** in your web browser.
2. Log in using the `ADMIN_EMAIL` and `ADMIN_PASSWORD` you set in the `.env` file.
3. Access the **Admin Dashboard** via the user menu.
4. From the dashboard, you can:
* Create new user accounts.
* Manage token limits and model access for individual users.
