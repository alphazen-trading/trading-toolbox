# MM Template

## Installation and General Information
### Pre-requisites
You will need to have the following installed:
1. [rye](rye-up.com/) -- For project management
2. [just](https://github.com/casey/just) -- similar to MakeFile, but on steroids
3. [nodemon](https://www.npmjs.com/package/nodemon) -- for development hot reload of scripts



### Setup
Clone the repo and then run the following:

```bash
just install
```

This will install the necessary python version as well as pip modules and scripts to execute with just.
It will also make the repo commitzen friendly.

### Running
You can create as many python scripts in `pyproject.toml` in the `[projects.scripts]` section.
If you want something more complex, it's recommended to use the `justfile`.

### Hooks and pre-commits
We use [pre-commit](https://pre-commit.com) to run before pushing to github/gitlab. (It is installed to you by default with rye).
It will do the following:

1. Lint with `ruff`
2. Run tests with `pytest`
3. Run `pyright`
4. PreCommit is used to validate the commit message

If any of these fails, you will be forbidden to push the branch until you fix the problems


### Todo
Need to add documentation information with mkdocs and add plugin to read from docstrings

----

## Docker: Grafana and Clickhouse
tl;dr
You can simple run `just local_docker`, and then head to [http://localhost:8000](http://localhost:8000) to check out your grafana dashboard.

There's a certain interest in using Clickhouse (CH) in the world of quant trading, due to the its capacity to handle billion of rows, compared to traditional SQL databases.
Clickhouse is fast because it forces the data to be tabular, using the apache arrow format, making it capable of streaming parquet files.
You can for sure dig in more online.

However, the goal of logging into a database, is in order to gather all data necessary to log the performance of our bots.
Grafana, opensearch, and other tools do a great job. Here again, grafana has a special place in the quant trading world.
On top of that, it's open source, and we can host it fully on premise, allowing better control.

### Docker
It's wise to run both grafana and CH inside a docker container. That's fast, and can be made in such a way that the containers are pre-configured to work nice with each other.
However, the downside is that grafana might not persist if you delete the container. This can be particularly frustrating if you spend hours working on your shiny dashboard, only to find it wiped with a `docker rm`!

We can mitigate this by forcing CH and grafana to write to a folder. There are some schenanigans in place, but we abstract that for you in the justfile.

---- 

## Rust in python

In order to achieve blazing fast tick to trades, many quants consider rust or c++. 
Rust is the newcomers favorite toy as it doesn't require work with c++, and is more elegant. 
Plus, tools like pyo3 make it incredibly pleasant to expose rust code as native python methods/classes, with very little overhead.
(In case you didn't know, `rye`, `pydantic`, `ruff`, and many of the other tools in the python ecosystem actually run rust behind the scene!)
