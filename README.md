# LLM OS

This project contains an initial implementation of the **LLM OS** proposed by
[Andrej Karpathy][karpathy].
He introduced it [in this post][post1] on [𝕏] and talks more about it in
[this post][post2] and [this video].

## Architecture

![LLM-OS Architecture][llm-os-arch]

> Learn more about LLM-OS in [Intro to Large Language Models][this video] by
[Andrej Karpathy][karpathy].

[karpathy]: https://karpathy.ai
[𝕏]: https://x.com/
[post1]: https://x.com/karpathy/status/1707437820045062561
[post2]: https://x.com/karpathy/status/1723140519554105733
[this video]: https://youtu.be/zjkBMFhNj_g?t=2535
[llm-os-arch]: ./res/images/llm-os-architecture.png

## Setup

### Create virtualenv

Create your virtualenv with built-in `venv` package.

```python
python -m venv .venv
```

Activate your environment.

```sh
source .venv/bin/activate
```

### Install dependencies

Install dependencies using `poetry`.

```sh
poetry install
poetry install --with dev  # for dev
```

### API Keys and Secrets

You have two options to create your API keys: using `.env` file or `streamlit`'s
secrets. Note that you can only use `streamlit` when running the `streamlit` app
locally or when deployed. However, `.env` is advised for local development.

- **Create your secrets with `.env`**

```sh
mv .env.example .env
```

Edit `.env` file.

```sh
OPENAI_API_KEY=sk-...
EXA_API_KEY=c0...
```

<!-- TODO: Use streamlit secrets for API keys. -->
- **Create your secrets & config with `streamlit`**

```sh
mkdir -p ./.streamlit/
touch ./.streamlit/secrets.toml  # for secret keys
touch ./.streamlit/config.toml   # for streamlit config
```

Edit `$CWD/.streamlit/secrets.toml` file.

```toml
OPENAI_API_KEY = "<get API key from platform.openai.com/api-keys>"
NEWS_API_KEY = "<get API key from https://newsapi.org/register>"
```

### Run PgVector

We use `PgVector` to provide long-term memory and knowledge to the LLM OS.
Please install [docker desktop] and run `PgVector` using either the helper script
or the `docker run` command.

[docker desktop]: https://docs.docker.com/desktop/install/mac-install/

- **Run using a helper script**

```sh
./run_pgvector.sh
```

- **OR run using the docker run command**

```sh
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  phidata/pgvector:16
```

## Usage

Start your `streamlit` application:

```sh
streamlit run home.py
```

## Contribution

You are very welcome to modify and use them in your own projects.

Please keep a link to the [original repository]. If you have made a fork with
substantial modifications that you feel may be useful, then please
[open a new issue on GitHub][issues] with a link and short description.

## License (MIT)

This project is opened under the [MIT][license] which allows very broad use for
both private and commercial purposes.

A few of the images used for demonstration purposes may be under copyright.
These images are included under the "fair usage" laws.

[original repository]: https://github.com/victor-iyi/llm-os
[issues]: https://github.com/victor-iyi/llm-os/issues
[license]: ./LICENSE
