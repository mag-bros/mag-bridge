# Zadanie: Wydzielenie Electrona do dedykowanego folderu "Sidecar"

**Kontekst projektu:**
- Projekt to aplikacja typu "All-in-one" (API + Frontend w Angularze).
- Frontend znajduje się w folderze `frontend/`.
- Środowisko deweloperskie (API + Angular) działa wewnątrz Dev Containera (Docker/Colima).
- Electron ma być uruchamiany wyłącznie na hostingu (macOS), łącząc się z kodem w kontenerze przez port 4200.

**Cel operacji:**
1. **Nowa struktura:** Stwórz folder `electron/`. Przenieś tam pliki odpowiedzialne za proces główny Electrona (np. `main.js`, `preload.js`).
2. **Izolacja zależności:** - Przenieś `electron`, `electron-builder` i inne paczki specyficzne dla Electrona z głównego `package.json` do nowo utworzonego `electron/package.json`.
   - W głównym `package.json` (używanym w Dev Containerze) usuń wszystkie zależności związane z Electronem, aby uniknąć błędów kompilacji pod Linuxem (brak bibliotek graficznych).
3. **Refaktoryzacja Angulara (Renderer):**
   - Usuń bezpośrednie importy z bibliotek `electron` lub `fs` w plikach `.ts` Angulara.
   - Zaimplementuj `ElectronService` w Angularze, który komunikuje się z systemem wyłącznie przez bezpieczny most `window.electronAPI`.
   - Dodaj definicje typów w `src/typings.d.ts`, aby TypeScript rozpoznawał obiekt `window.electronAPI`.
4. **Konfiguracja Mostu (Context Bridge):**
   - W `electron/preload.js` użyj `contextBridge` i `ipcRenderer`, aby wystawić bezpieczne funkcje systemowe (np. dostęp do plików na Macu) dla Angulara.
5. **Konfiguracja Main Process (`main.js`):**
   - Zaktualizuj ścieżkę ładowania: w trybie deweloperskim Electron ma ładować `http://localhost:4200`.
   - W trybie produkcyjnym ma ładować zbudowane pliki Angulara z folderu `dist/`.
   - Ustaw `contextIsolation: true` oraz `nodeIntegration: false` dla maksymalnego bezpieczeństwa.

**Wynik końcowy:**
Dostarcz zaktualizowaną strukturę plików, zawartość `electron/package.json`, kod `preload.js` z przykładową funkcją systemową oraz kod `ElectronService` dla Angulara.