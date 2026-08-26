# Home LLM

Deploy your own LLM chat website from home!   
I built this website to have a standard LLM chat interface (like https://claude.ai, https://gemini.google.com/, or any other LLM provider) for my VLLM instances I have at home, and for the free API key's I have sitting around. 
 
## Quick Start

### 1. Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine installed.
* *(Optional)* NVIDIA Drivers and [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) if you will launch the VLLM instance on the same machine as the website, which is how I do it.

### 2. Configuration
Clone the repository and set up your environment variables:

```bash
git clone [https://github.com/yigittuncer07/home-llm](https://github.com/yigittuncer07/home-llm)
cd home-llm
cp .env.example .env

```

Open `.env` in a text editor and fill in your details.

* Set your `ADMIN_EMAIL` and `ADMIN_PASSWORD` (used for your initial login). Or just leave them as is.

Configure your available models by editing `app/backend/models.yaml`.

* If using the local vLLM container, set the `api_base` to `http://vllm:8001/v1`. If running on another machine, set accordingly.

### 3. Deployment

**Option A: Deploy WITHOUT local models (External APIs only)**
If you are using remote API's or if VLLM is running on another machine, run like this to run without VLLM:

```bash
docker compose up -d

```

**Option B: Deploy WITH local models (Requires NVIDIA GPU)**
If you want to host an open-source model directly on this machine using your GPU, activate the `local-gpu` profile. Be sure to set the backend/models.yaml file to have the model you want, along with variables in your .env file. The default model is Qwen3.5-0.8B.

```bash
docker compose --profile local-gpu up -d

```

### 4. First Steps

1. Navigate to **http://localhost** in your web browser.
2. Log in using the `ADMIN_EMAIL` and `ADMIN_PASSWORD` you set in the `.env` file.
3. Access the **Admin Dashboard** via the user menu.
4. From the dashboard, you can:
* Create new user accounts.
* Manage token limits and model access for individual users.