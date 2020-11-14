release/bojos_ships.zip: kalman/*.ipynb traces/*.ipynb data/bojos2020.csv
	mkdir -p release
	cp kalman/*.ipynb release/
	cp traces/*.ipynb release/
	nbstripout release/*.ipynb
	cp data/bojos2020.csv release/
	zip -j bojos_ships.zip release/*.ipynb
	mv bojos_ships.zip release/

clean: release/bojos_ships.zip
	rm release/bojos_ships.zip
