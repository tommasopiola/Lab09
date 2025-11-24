from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # TODO: Aggiungere eventuali altri attributi
        self._tour_disponibili = []  # Lista di supporto per la ricorsione

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()

    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """

        # TODO
        relazioni = TourDAO.get_tour_attrazioni()
        if relazioni:
            for relazione in relazioni:

                tour_obj = self.tour_map.get(relazione["id_tour"])
                attr_obj = self.attrazioni_map.get(relazione["id_attrazione"])

                if tour_obj and attr_obj:
                    # Collegamento bidirezionale
                    tour_obj.attrazioni.add(attr_obj)  # Aggiungo l'attrazione al Tour
                    attr_obj.tour.add(tour_obj)  # Aggiungo il Tour all'Attrazione


    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        # filtro i tour della regione selezionata
        self._tour_disponibili = [
            t for t in self.tour_map.values() if t.id_regione == id_regione
        ]

        # avvio la ricorsione
        # passo anche max_giorni e max_budget per comodità
        self._ricorsione(0, [], 0, 0, 0, set(), max_giorni, max_budget)

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    # aggiungo max_giorni e max_budget nei parametri della funzione
    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set, max_giorni: int, max_budget: float):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno

        # controllo se ho trovato una soluzione migliore
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = list(pacchetto_parziale)
            self._costo = costo_corrente

        # caso Base: Ho esaminato tutti i tour disponibili
        if start_index >= len(self._tour_disponibili):
            return

        # recupero il tour corrente
        t = self._tour_disponibili[start_index]

        # verifica Vincoli:
        # a) Budget (se definito)
        vincolo_budget_ok = (max_budget is None) or (costo_corrente + t.costo <= max_budget)
        # b) Durata (se definita)
        vincolo_durata_ok = (max_giorni is None) or (durata_corrente + t.durata_giorni <= max_giorni)
        # c) Attrazioni Uniche (intersezione tra set deve essere vuota)
        vincolo_attrazioni_ok = attrazioni_usate.isdisjoint(t.attrazioni)

        if vincolo_budget_ok and vincolo_durata_ok and vincolo_attrazioni_ok:

            # nuovi dati per la chiamata ricorsiva
            nuovo_pacchetto = pacchetto_parziale + [t]
            nuova_durata = durata_corrente + t.durata_giorni
            nuovo_costo = costo_corrente + t.costo
            # calcolo valore culturale del singolo tour sommando le sue attrazioni
            valore_tour = sum(a.valore_culturale for a in t.attrazioni)
            nuovo_valore = valore_corrente + valore_tour
            nuove_attrazioni = attrazioni_usate | t.attrazioni  # Unione dei set

            self._ricorsione(start_index + 1, nuovo_pacchetto, nuova_durata, nuovo_costo, nuovo_valore, nuove_attrazioni, max_giorni, max_budget)

        # procedo senza aggiungere questo tour
        self._ricorsione(start_index + 1, pacchetto_parziale, durata_corrente, costo_corrente, valore_corrente, attrazioni_usate, max_giorni, max_budget)
