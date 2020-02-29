# Publish Project to PyPi
Here are the steps that are necessary to publish a new version

Update Github



Build wheel
```
python setup.py sdist bdist_wheel
```

Publish
```
twine upload dist/*
```

