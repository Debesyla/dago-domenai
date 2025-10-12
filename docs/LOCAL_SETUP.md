# Local development setup (macOS)

This repo uses a `.env` file so you can connect to a local Postgres during development and to the server DB in production without changing code.

## 1) Install PostgreSQL
- Recommended: Postgres.app or Homebrew
- With Homebrew:

```bash
brew install postgresql@16
brew services start postgresql@16
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Create DB and user matching the example credentials (or change `.env`):

```bash
createuser -s domenai || true
createdb -O domenai domenai || true
psql -d postgres -c "ALTER USER domenai WITH PASSWORD 'larakniaukialiauliau';"
```

## 2) Create and fill `.env`

```bash
cp .env.example .env
# edit if needed; default points to postgresql://domenai:larakniaukialiauliau@localhost:5432/domenai
```

## 3) Apply schema and seed data

```bash
source .env  # load DATABASE_URL into your shell
echo "$DATABASE_URL"  # sanity check: should print a postgres:// URL
psql "$DATABASE_URL" -f db/schema.sql
psql "$DATABASE_URL" -f db/seed.sql
```

## 4) Create a virtualenv and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
# Install only app dependencies (avoids OS-specific packages in requirements.txt)
pip install -r requirements.app.txt
```

## 5) Test the connection/script

```bash
python src/db_test_insert.py
```

You should see an inserted `results` row for `test.lt`.

## Notes
- `.env` is git-ignored and safe to configure per environment.
- On the server, create the same `.env` but point to the server DB; scripts will work unchanged.
- If `psycopg2-binary` fails on macOS ARM: try `brew install postgresql` then reinstall, or consider using psycopg3 in the future.

## Troubleshooting on macOS (zsh)

- Command not found for `psql`, `createuser`, or `createdb`:
	- If installed via Homebrew on Apple Silicon (M1/M2/M3), add Postgres to PATH:
		```bash
		echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
		source ~/.zshrc
		```
	- If installed via Homebrew on Intel Macs:
		```bash
		echo 'export PATH="/usr/local/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
		source ~/.zshrc
		```
	- If using Postgres.app, add its binaries to PATH:
		```bash
		echo 'export PATH="/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH"' >> ~/.zshrc
		source ~/.zshrc
		```
	- Verify:
		```bash
		which psql
		psql --version
		```

- If the service isn't running:
	```bash
	brew services start postgresql@16
	```

- If the `domenai` user already exists, the createuser step will be skipped because of `|| true`.
