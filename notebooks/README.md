# yamm-notebooks

This repos houses one notebook for showing how to interact with the yamm package.

### setup

Create an environment with jupyter, something like:

```
conda create -n jupyter python=3.8 jupyter-lab
```

Install yamm according to [the setup instructions](https://github.com/NREL/yamm#setup)

Make yamm accesible as a jupyter kernel

```
conda activate <environment-with-yamm>
conda install ipykernel
ipython kernel install --user --name=yamm
conda deactivate
```

Launch jupyter and pick the `yamm` kernel option

```
jupyter lab
```