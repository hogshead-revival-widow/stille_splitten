# Überblick

Trennt Audio-Files auf denen Beiträge durch unüblich lang anhaltende Stille getrent sind. Als Ergebnis werden die berechneten Start- und Endpunkte der Beiträge als Timecode ausgegeben. 

# Installation

1. Repo klonen oder runterladen
2. `cd <Verzeichnis in das entpackt wurde>`
3. `python setup.py install`

`stille_splitten` ist nun als Kommandozeilen-Befel zugänglich.

## Voraussetzung

[ffmpeg](https://ffmpeg.org/) muss auf dem System vorliegen und in `PATH` aufzufinden sein.
Alternativ ist der Pfad zu FFMPEG in `settings.py` anzugeben.

## Einschränkung

Getestet wurde das Skript nur mit Python 3.8.2 auf macOS und Windows 10.

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
        {
            "start": "00:00:00.000", 
            "end": "00:04:18.232",
            "duration": "00:04:18.231",
            "korpus_nr": 1,
            "sicherheit": 100,
            "datei": "55-W5023544-Erwartung_falsch"
        }
```

Dabei bedeutet:
    * **start**: den Beginn der Sequenz
    * **end**: das Ende der Sequenz
    * **duration**: Sequenz-Dauer 
    * **korpus_nr**: fortlaufende Position der Sequenz im File
    * **sicherheit**: 2 bis 100
        * 100: Sequenzmenge, der diese Sequenz zugehört, entspricht der Anzahl der erwarteten Sequenzen
        * 1-8: Häufigkeit mit der identische Sequenzmengen, wie die, zu der diese Sequenz gehört, 
        im File in unterschiedlichen Durchläufen gefunden wurde
    * **datei**: Datei in der diese Sequenz gefunden wurde (ohne Endung)

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

Die Einstellung der genutzten Pfade und weitere Optionen ist bei Bedarf in
`settings.py` möglich.

# Warum?

## Ausgangsproblem

Bei der Rückwärtsdigitalisierung von Audiomedien werden Sammelbänder digitalisiert. Auf diesen sind Einzelbeiträge durch unüblich lange Sequenzen von Stille getrennt. Liegen für diese Bänder noch Nachweise vor, kann aus diesen die Anzahl der enthaltenen Beträge abgelesen werden. Nicht immer ist das der Fall zum Teil sind sie unvollständig. Zudem fehlen in aller Regel Timecodes zu den Beiträgen, sind falsch oder zu ungenau. Das ist für eine zufriedenstellende Archivierung ärgerlich -- oder ziemlich zeitaufwendig manuell zu fixen.

## Lösung

Dieses Skript generiert daher aus einem Audiofile mögliche Beitrags-Sequenzen, um digitalisierte Audiofiles besser im Archiv zugänglich zu machen. 

Gibt es eine Vermutung, wieviele Sequenzen auf dem Band sind, prüft das Skript, ob die gefundenen Sequenzanzahl dieser Erwartung entspricht. Wenn eine passende Sequenzmenge gefunden wurde, wird die Suche abgebrochen. 

Ist die Anzahl unbekannt, werden nach insgesamt acht Durchgängen mit unterschiedlichen Parametern die gefundenen Sequenzen verglichen. Gleichen sie sich hinreichend genau (max. 10 Sekunden Unterschied), gelten Sequemzmengen als gleich. In der Ausgabe wird notiert, wie oft die gleiche Sequenzmenge gefunden wird. Bisher scheinen die Ergebnisse ab etwa drei identischen Mengen zuverlässig zu sein. 

Zur besseren Weiterverarbeitung werden die Ergebnisse in JSON und als Excel-Datei ausgegeben.

## Alternativen

- [pydub](https://github.com/jiaaro/pydub) bietet mit `detect_silence` eine ähnliche Funktion, baut ebenfalls auf ffmpeg auf, trifft den Anwendungsfall aber nur teilweise
- [ffmpeg direkt nutzen](http://underpop.online.fr/f/ffmpeg/help/silencedetect.htm.gz), ffmpeg bietet `silencedetect`, auf das hier aufgebaut wird
- [Audacity silence finder](https://manual.audacityteam.org/man/silence_finder_setting_parameters.html) 
