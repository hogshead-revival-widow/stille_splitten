# Überblick

Trennt Audio-Files auf denen Beiträge durch unüblich lang anhaltende Stille getrennt sind (z. B. digitalisierte Sammelbänder). Als Ergebnis werden die berechneten Start- und Endpunkte der Beiträge als Timecode ausgegeben. 

# Installation

1. Repo klonen oder runterladen
2. `cd <Verzeichnis in das entpackt wurde>`
3. `python -m pip install -e .`

`stille_splitten` ist nun als Kommandozeilen-Befel zugänglich.

## Voraussetzung

[ffmpeg](https://ffmpeg.org/) muss auf dem System vorliegen und in `PATH` aufzufinden sein.

Alternativ ist der Pfad zu FFMPEG in `settings.py` anzugeben.

# Wo finde ich was?

Beim ersten Durchlauf wird in `Desktop/` das Verzeichnis `stille_splitten` angelegt.

Es hat die folgenden Verzeichnisse:
   * `ergebnisse`: Hier werden die Ergebnisse als JSON/Excel-Dateien hinterlegt
   * `stapelverarbeitung`: Hier hinterlegte Dateien können über `stille_splitten stapel` durchsucht werden (siehe unten)

## Log

Das Log findet sich in `Desktop/stille_splitten/stille_splitten.log`.

# Benutzung (Datei)

Die Datei `abc.mp3` soll untersucht werden, erwartet werden 3 Sequenzen, die durch Stille getrennt sind:
  * `stille_splitten datei abc.mp3 3`

Ausgabe:
  * in der Konsole wird der Fund als sicher oder wahrscheinlich eingeschätzt
  * in `stille_splitten/ergebnisse` sind die Ergebnisse als Exceldatei und JSON-formatiert zu finden

# Benutzung (Stapelverarbeitung)

Alle Dateien im Verzeichnis `xyz/` sollen untersucht werden, es enthält z. B. die Datei `13-abc.mp3`. Durch die Angabe von "13-" im Dateinamen wird von dieser Datei angenomen, dass sie 13 Sequenzen enthält.
  * `stille_splitten stapel xyz`

Ausgabe:
  * in Konsole wird der Fund als sicher oder wahrscheinlich eingeschätzt
  * in `stille_splitten/ergebnisse` sind die Ergebnisse als Exceldatei und JSON-formatiert zu finden in einer Sammeldatei für den gesamten Duchlauf


# Beispiel: Sequenz gefunden

```
[
  {
    "start": "00:00:00.000", 
    "end": "00:04:18.232",
    "duration": "00:04:18.231",
    "sequence_nr": 1,
    "probability": 100,
    "in_file": "55-W5023544-Erwartung_falsch"
  },...
 ]
```

Dabei bedeutet:
  * **start**: den Beginn der Sequenz
  * **end**: das Ende der Sequenz
  * **duration**: Sequenz-Dauer 
  * **sequence_nr**: fortlaufende Position der Sequenz im File
  * **probability**: Wert zwischen `1` und der maximalen Menge an Durchläufen (vgl. `SETTINGS['ffmpeg_options']`) *oder* `100`
    * 100: Sequenzmenge, der diese Sequenz zugehört, entspricht der Anzahl der erwarteten Sequenzen
    * 1-4: Häufigkeit mit der identische Sequenzmengen, wie die, zu der diese Sequenz gehört,  im File in unterschiedlichen Durchläufen gefunden wurde
  * **in_file**: Datei in der diese Sequenz gefunden wurde (ohne Endung)

# Hilfe

```
Usage: stille_splitten [OPTIONS] COMMAND [ARGS]...

  Findet länger anhaltende Stille in Audiofiles und generiert daraus
  Sequenzen.

Options:
  --version   Version anzeigen und beenden.
  -h, --help  Show this message and exit.

Commands:
  datei   Sucht in <Datei> nach Sequenzen, optional mit der Angabe der Anzahl
          der erwarteten Sequenzen (<Erwartung>).
          
          Beispielaufruf: `stille_splitten datei "abc.mp3"`
          Aufruf mit Erwartung: `stille_splitten datei "abc.mp3" 13`
          
  stapel Beginnt Stapelverarbeitung mit allen Files im Stapelverzeichnis.
          
            * Default-Verzeichnis:
             - `~/Desktop/stille_splitten/stapelverarbeitung`.
            * Namenskonvention der Dateien im Verzeichnis:
             - `<Erwartung>-W5023536.mp2` (z. B.: 13-W5023536.mp2)
            * Gibt es keine mit einem Bindestrich getrennte Zahl im Dateinamen,
              wird ohne Erwartung gesucht.
            
            Beispielaufruf: `stille_splitten stapel`
            Durchsuche anderes Verzeichnis: `stille_splitten stapel "aus_diesem_verzeichnis"`
```
## Hilfe: Kommando: `stapel`

```
Usage: stille_splitten stapel [OPTIONS] [VERZEICHNIS]

  Beginnt Stapelverarbeitung mit allen Files im Stapelverzeichnis.  Wenn ein
  Wert für <Verzeichnis> angegeben wird, wird in diesem Verzeichnis gesucht.

Options:
  --debug     Logge ausführlich.
  -h, --help  Show this message and exit.
```

## Hilfe: Kommando: `datei`

```
Usage: stille_splitten datei [OPTIONS] DATEI [ERWARTUNG]

  Sucht in <Datei> nach Sequenzen, optional mit der Angabe der Anzahl der
  erwarteten Sequenzen (<Erwartung>)

Options:
  --debug     Logge ausführlich.
```

# Konfiguration

Die Einstellung der genutzten Pfade ist bei Bedarf in
`settings.py` möglich. Es finden sich dort weitere Optionen.

# Warum?

## Ausgangsproblem

Bei der Rückwärtsdigitalisierung von Audiomedien werden Sammelbänder digitalisiert. Auf diesen sind Einzelbeiträge durch unüblich lange Sequenzen von Stille getrennt. Liegen für diese Bänder noch Nachweise vor, kann aus diesen die Anzahl der enthaltenen Beträge abgelesen werden. Nicht immer ist das der Fall, zum Teil sind sie unvollständig. Zudem fehlen in aller Regel Timecodes zu den Beiträgen, sind falsch oder ungenau. Das ist für eine zufriedenstellende Archivierung ärgerlich -- oder ziemlich zeitaufwendig manuell zu fixen.

## Lösung

Dieses Skript generiert daher aus einem Audiofile mögliche Beitrags-Sequenzen.

Wird eine bestimmte Anzahl Sequenzen auf dem Band vermutet, prüft das Skript, ob die gefundenen Sequenzanzahl dieser Erwartung entspricht. Wenn eine passende Sequenzmenge gefunden wurde, wird die weitere Suche abgebrochen. 

Ist die Anzahl unbekannt, werden nach mehreren Durchgängen (vgl. `SETTINGS['ffmpeg_options']` in `settings.py`) mit unterschiedlichen Parametern die gefundenen Sequenzen verglichen. Gleichen sie sich hinreichend genau (max. 10 Sekunden Unterschied), gelten Sequemzmengen als gleich. In der Ausgabe wird notiert, wie oft die gleiche Sequenzmenge gefunden wird. Ab zwei gleichen Mengen scheinen die Ergebnisse zuverlässig.

Zur Weiterverarbeitung werden die Ergebnisse in JSON und als Excel-Datei ausgegeben.

## Alternativen

- [pydub](https://github.com/jiaaro/pydub) bietet mit `detect_silence` eine ähnliche Funktion, baut ebenfalls auf ffmpeg auf, trifft den Anwendungsfall aber nur teilweise
- [ffmpeg direkt nutzen](http://underpop.online.fr/f/ffmpeg/help/silencedetect.htm.gz), ffmpeg bietet `silencedetect`, auf das hier aufgebaut wird
- [Audacity silence finder](https://manual.audacityteam.org/man/silence_finder_setting_parameters.html) (nicht getestet, GUI)
