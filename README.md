# publictransport test push

### Interactive webapp that shows you how far public transport can get you in a particular amount of time?

#### Check out this link to see a video of the functions: https://www.dropbox.com/s/nfrqtfcrvbc6kxw/video.mp4?dl=0

### To try the webapp:
#### Use this Link: https://publictransport.caleydoapp.org/

# Run Server
open cmd and create a new virtual environment for the dependencies

```bash
python -m venv .venv
```

activate it

```bash
# Ubuntu
source .venv/bin/activate

# Windows (cmd)
.\.venv\Scripts\activate
```

install dependencies (TODO: create requirements file)

```
pip install uvicorn
pip install fastapi
pip install pydantic
pip install geojson
pip install shapely
pip install pandas

```


```
uvicorn main:app --reload

```

# Run Front End
open a powershell terminal and navigate to /myapp

install dependencies

```bash
npm install
```

run development server

```bash
npm run dev
```
