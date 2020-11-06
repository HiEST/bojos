release/bojos_ships.zip: kalman/*.ipynb traces/*.ipynb
	mkdir -p release
	cp kalman/*.ipynb release/
	cp traces/*.ipynb release/
	zip bojos_ships.zip release/*.ipynb
	mv bojos_ships.zip release/
