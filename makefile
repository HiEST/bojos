release/bojos_ships.zip: kalman/*.ipynb traces/*.ipynb data/bojos2020.csv
	mkdir -p release
	cp kalman/*.ipynb release/
	cp traces/*.ipynb release/
	cp kalman/*template* release/
	cp traces/*template* release/
	nbstripout release/*.ipynb
	cp data/bojos2020.csv release/
	zip -j bojos_ships.zip release/*.ipynb release/*.py
	mv bojos_ships.zip release/
	rm release/*.{py,ipynb}

clean: release/bojos_ships.zip
	rm release/bojos_ships.zip
