# NĪ ziņu monitors → Telegram

Ievāc jaunumus no 47 Latvijas NĪ, būvniecības un arhitektūras avotiem un sūta tos
Telegram čatā, kurā esi tikai tu un bots. Darbojas GitHub serveros - katru stundu,
bez maksas, arī tad, kad tavs dators ir izslēgts.

Avotu saraksts un kāpēc tieši šie - `wiki/ni-jaunumu-portali.md`.

---

# CEĻVEDIS NO NULLES

Nekas nav jāinstalē. Nekāda komandrinda. Viss notiek pārlūkā un Telegram.
Kopā ~25 minūtes, no kurām 10 ir gaidīšana.

**Kur atrodas faili, ko augšupielādēsi:**
`C:\Users\blaus\Desktop\LAIDA-Wiki\riki\zinu-monitors\`

Atver šo mapi Explorer un atstāj vaļā - tā vajadzēs 3. daļā.

---

## A DAĻA · Telegram bots (5 minūtes)

### A1. Uztaisi botu

Atver Telegram (telefonā vai datorā - vienalga). Meklētājā ieraksti **@BotFather**
un atver to. Tas ir oficiālais Telegram bots ar zilu ķeksīti.

Nospied **START**, tad uzraksti:

```
/newbot
```

BotFather prasīs divas lietas:

1. **Vārdu** - ko redzēsi čatā. Ieraksti: `AIS zinu monitors`
2. **Lietotājvārdu** - jābeidzas ar `bot` un jābūt unikālam visā Telegram.
   Pamēģini: `ais_zinu_monitors_bot`. Ja aizņemts, pieliec ciparu: `ais_zinu_monitors2_bot`

### A2. Saglabā tokenu

BotFather atbildēs ar tekstu, kurā būs rinda apmēram šāda:

```
8123456789:AAFm-xYz1234567890abcdefGHIJKLMNOPqrs
```

**Tas ir tokens.** Nokopē to kaut kur pagaidām - Notepad, piezīmēs, vienalga.
Vēlāk to ieliksi GitHub un no piezīmēm izdzēsīsi.

⚠️ Tokens = pilna vara pār botu. Nesūti to nevienam, neliec failā, neliec čatā.

### A3. Uzraksti botam

Telegram meklētājā ieraksti sava jaunā bota lietotājvārdu (`ais_zinu_monitors_bot`),
atver to un nospied **START**.

**Šis solis ir obligāts.** Telegram neļauj botam rakstīt pirmajam. Kamēr tu neesi
tam uzrakstījis, tas tev sūtīt nevar.

### A4. Uzzini sava čata numuru

Atver pārlūkā šo adresi, tikai `<TOKENS>` vietā ieliec savu tokenu no A2:

```
https://api.telegram.org/bot<TOKENS>/getUpdates
```

Piemēram tas izskatīsies tā:
`https://api.telegram.org/bot8123456789:AAFm-xYz.../getUpdates`

Lapā būs teksts, kurā meklē `"chat":{"id":`. Aiz tā ir skaitlis:

```json
"chat":{"id":123456789,"first_name":"Rihards"
```

**`123456789` ir tavs chat ID.** Nokopē arī to blakus tokenam.

> **Ja lapā redzi tikai `{"ok":true,"result":[]}`** - tas nozīmē, ka A3 solis nav
> izdarīts. Atgriezies Telegram, uzraksti botam vēl kaut ko (piem. `sveiks`),
> un pārlādē lapu.

Tagad tev ir divas lietas: **tokens** un **chat ID**. A daļa gatava.

---

## B DAĻA · GitHub (10 minūtes)

GitHub ir vieta, kur dzīvos skripts un kas to palaidīs katru stundu. Tev tur nekas
nav jāprogrammē - tikai jāieliek faili un divi noslēpumi.

### B1. Uztaisi kontu

Ja tev GitHub konta nav: **github.com** → **Sign up**. E-pasts, parole,
lietotājvārds. Apstiprini e-pastu. Bezmaksas plāns pietiek pilnībā.

Ja konts ir - vienkārši ielogojies.

### B2. Uztaisi repozitoriju

Augšā pa labi **+** → **New repository**.

Aizpildi tā:

| Lauks | Ko likt |
|---|---|
| Repository name | `ni-zinu-monitors` |
| Description | `NI zinu monitors uz Telegram` |
| Public / Private | **Public** - skaties piezīmi zemāk |
| Add a README file | **NEATĶERTU** |
| .gitignore / license | nekas |

Nospied **Create repository**.

> **Public vai Private?**
> Kodā nekā slepena nav - tokens glabājas atsevišķi (B4 solis), ne failos.
> **Public** ir ieteicams, jo GitHub tad dod neierobežotu darbības laiku.
> Private repo dod 2000 minūtes mēnesī, un stundas ritms tās gandrīz izsmeļ.
> Ja tomēr gribi Private, tad C daļas beigās nomaini grafiku uz ik pēc 2 stundām.

### B3. Augšupielādē failus

Tukšajā repozitorijā redzēsi rindu **"uploading an existing file"** - klikšķini uz tās.
(Ja neredzi: **Add file** → **Upload files**.)

Tagad atver Explorer mapi `C:\Users\blaus\Desktop\LAIDA-Wiki\riki\zinu-monitors\`

**Iezīmē visu, kas tur ir** (Ctrl+A) un **ievelc pārlūka logā** melnajā laukumā.

Failiem jābūt šiem:

```
.github          (mape - tajā iekšā workflows\monitor.yml)
.gitignore
README.md
discover.py
monitor.py
requirements.txt
sources.yaml
```

⚠️ **Svarīgi:** ievelc mapes **saturu**, ne pašu mapi `zinu-monitors`. Ja repozitorijā
parādās mape `zinu-monitors` un tajā iekšā faili, tad ir nepareizi - izdzēs un
sāc no jauna, ievelkot atsevišķos failus.

⚠️ Ja `__pycache__` mape ir līdzi - to var mierīgi izlaist, tā nav vajadzīga.

Apakšā nospied **Commit changes**.

Pēc dažām sekundēm repozitorijā redzēsi visus failus. Pārliecinies, ka redzi
mapi `.github` - bez tās nekas nestrādās.

### B4. Ieliec tokenu un chat ID

Repozitorijā augšā: **Settings** (zobratiņš, pašā labajā malā).

Kreisajā izvēlnē: **Secrets and variables** → **Actions**.

Nospied zaļo **New repository secret**. Divas reizes, katrai lietai:

**Pirmā:**
- Name: `TELEGRAM_BOT_TOKEN`
- Secret: tokens no A2 soļa
- **Add secret**

**Otrā:**
- Name: `TELEGRAM_CHAT_ID`
- Secret: skaitlis no A4 soļa
- **Add secret**

Nosaukumiem jābūt tieši tādiem - lielie burti, apakšsvītras. Ja kļūdīsies, skripts
tos neatradīs.

Tagad no Notepad piezīmēm tokenu vari izdzēst.

---

## C DAĻA · Pirmā palaišana (10 minūtes, no kurām 8 gaidīšana)

### C1. Ieslēdz Actions

Repozitorijā augšā: cilne **Actions**.

Ja parādās zaļa poga **"I understand my workflows, go ahead and enable them"** -
nospied to. Ja neparādās, viss jau ir kārtībā.

Kreisajā pusē redzēsi **NI zinu monitors**. Klikšķini uz tā.

### C2. Pārbaude - `dry-run`

Pa labi: **Run workflow** (poga ar bultiņu).

Atveras neliela izvēlne. Laukā **Režīms** izvēlies **`dry-run`**.
Nospied zaļo **Run workflow**.

Pēc ~10 sekundēm sarakstā parādīsies jauna rinda ar dzeltenu apli - tas nozīmē
"strādā". Pagaidi 3-5 minūtes, līdz aplis kļūst zaļš.

**Kas tikko notika:** skripts apgāja visus 47 avotus, saskaitīja, cik rakstu no
katra dabū, un **neko nenosūtīja**.

**Apskati rezultātu:** klikšķini uz rindas → **monitor** → **Palaist monitoru**.
Atveras logs. Ritini līdz apakšai, kur ir saraksts:

```
=== 312 jauni raksti ===
   LSM: 4
   Delfi: 2
   building.lv: 11
 ! abc.lv: NEIZDEVĀS
   A4D: 8
   ...
```

Rindas ar `!` un `NEIZDEVĀS` ir avoti, kas neatbildēja. **Tas ir normāli** - daļa
Latvijas lapu ir uztaisītas tā, ka robots tur neko neredz. Ja strādā 30 un vairāk
no 47, viss ir labi. Ko darīt ar pārējiem - D daļā, bet tas nav steidzami.

### C3. Iesēšana - `seed`

**Šo soli nedrīkst izlaist.**

Vēlreiz **Run workflow**, šoreiz režīms **`seed`** → **Run workflow**.

Pagaidi, līdz aplis kļūst zaļš (3-5 min).

**Kas tikko notika:** skripts atzīmēja visus ~312 šobrīd esošos rakstus kā
"jau redzētus" un neko nenosūtīja. Bez šī soļa pirmajā automātiskajā ciklā tavs
telefons saņemtu 300 paziņojumus pēc kārtas.

### C4. Gaidi

Viss. Tālāk nekas nav jādara.

Katru stundu septītajā minūtē (:07) GitHub palaidīs skriptu pats. Ja kaut kur būs
parādījies jauns raksts, tas ienāks Telegram šādā formātā:

```
🏗 building.lv
Jauns būvniecības projekts Rīgā tiek uzsākts rudenī
```

Virsraksts ir saite. Emoji rāda kategoriju:

📰 ziņu portāli · 💼 biznesa mediji · 🏗 būvniecība · 📐 arhitektūra
🏠 NĪ portāli · 📊 aģentūras · 🏦 bankas · 🏛 oficiālie

**Pirmā ziņa var atnākt pēc 20 minūtēm vai pēc 5 stundām** - atkarīgs no tā, kad
kāds portāls kaut ko publicēs. Ja līdz nākamajai dienai nav atnākusi neviena,
tad kaut kas nav kārtībā - skaties D daļu.

### C5. Ja repo ir Private - nomaini grafiku

Izlaid šo, ja repo ir Public.

Repozitorijā: **.github** → **workflows** → **monitor.yml** → zīmuļa ikona (Edit).

Atrodi rindu:

```yaml
    - cron: "7 * * * *"
```

Nomaini uz:

```yaml
    - cron: "7 */2 * * *"
```

Apakšā **Commit changes**. Tagad skripts iet ik pēc divām stundām un GitHub
minūšu limitā ietilpsi mierīgi.

---

## D DAĻA · Kad kaut kas nestrādā

### Telegram neatnāk nekas

**1. Vai workflow vispār iet?** Actions cilne - vai pēdējās stundās ir zaļās rindas?
- Nav nevienas rindas → Actions nav ieslēgts, atgriezies pie C1.
- Rindas ir sarkanas → klikšķini uz sarkanās, skaties, kurā solī nokrita.

**2. Sarkans "Palaist monitoru" ar `trūkst TELEGRAM_BOT_TOKEN`**
→ Secrets nav ielikti vai nosaukumi ir ar kļūdu. Atgriezies pie B4.

**3. Zaļš, logā rakstīts `0 jauni raksti`, un tā vairākas stundas**
→ Tas var būt pilnīgi normāli naktī un brīvdienās. Pagaidi darba dienas rītu.

**4. Zaļš, logā redzi `Nosūtīts: 5`, bet Telegram ir tukšs**
→ Chat ID ir nepareizs. Atgriezies pie A4 un pārbaudi skaitli.
   Ja tas sākas ar mīnusu (`-100...`), tad esi paņēmis grupas ID, ne savu.

### Kāds avots rāda NEIZDEVĀS

Nav jālabo uzreiz - pārējie strādā. Kad būs laiks, trīs iemesli pēc biežuma:

**Lapa uzbūvēta ar JavaScriptu.** Robots redz tukšu lapu. Latvijā tas ir bieži.
Vispirms pārbaudi, vai lapai tomēr nav RSS: atver pārlūkā `https://tālapa.lv/feed/`.
Ja parādās XML teksts - tas ir RSS. Tad `sources.yaml` tam avotam pieliec rindu
`feed: https://tālapa.lv/feed/`. Ja tukšums vai kļūda - šo avotu labāk izmest.

**Nepareiza adrese konfigurācijā.** Atver avota ziņu lapu pārlūkā, uzklikšķini uz
viena raksta, paskaties tā adresi. Ja tā ir `https://x.lv/lv/aktualitates/2026/kaut-kas`,
tad `sources.yaml` tam avotam jābūt `link_contains: "/aktualitates/"`.

**Lapa bloķē robotus.** Neko nevar darīt, izmet no saraksta.

Labot var tieši GitHub - atver `sources.yaml`, zīmuļa ikona, izmaini, **Commit changes**.

### Nāk par daudz nevajadzīgā

Divas skrūves `sources.yaml` failā:

**Sašaurini atslēgvārdus.** `keywords` sarakstā `ipasum` ir plašs - tas ķer arī
"Zviedrijā atsavina Krievijas pilsoņa īpašumu". Izmet to rindu, un troksnis
samazināsies uz pusi.

**Izslēdz avotu.** Ieliec `#` visu tā bloka rindu priekšā. Vai vienkārši izdzēs bloku.

### Nāk par maz

`sources.yaml` → `settings` → `max_per_source: 12` uz `20`, un `max_per_run: 25` uz `40`.

---

## E DAĻA · Ikdiena

### Mainīt biežumu

`.github/workflows/monitor.yml`, rinda `cron`. **Laiks ir UTC** - Rīga vasarā ir
UTC+3, ziemā UTC+2.

| Gribu | cron |
|---|---|
| Katru stundu | `7 * * * *` |
| Ik pēc 2 stundām | `7 */2 * * *` |
| Ik pēc 3 stundām | `7 */3 * * *` |
| Divreiz dienā, ~9:00 un ~18:00 vasarā | `7 6,15 * * *` |

### Pievienot avotu

`sources.yaml`, jauns bloks jebkurā vietā saraksta iekšā:

```yaml
  - id: jaunais
    name: "Jaunais medijs"
    home: https://jaunais.lv/
    auto: true          # lai pats pamēģina atrast RSS
    filter: false       # true, ja lapa raksta arī par visu citu
    category: buvnieciba
```

Atstarpes ir svarīgas - divi tukšumi pirms `-`, četri pirms pārējām rindām.

### Palaist pēc pieprasījuma

Actions → NI zinu monitors → **Run workflow** → režīms `normal`. Nav jāgaida stunda.

### Ja gribi visu sākt no nulles

Izdzēs failu `seen.json` (repozitorijā, zīmuļa vietā atkritumu tvertnes ikona),
tad palaid `seed`. Vēsture ir notīrīta.

---

# TEHNISKĀ DAĻA

## Kā tas ievāc

Katram avotam skripts mēģina pēc kārtas:

1. **Zināms RSS** (`feed:` konfigurācijā) - visdrošākais.
2. **Automātiska RSS meklēšana** (`auto: true`) - paskatās lapas `<link rel="alternate">`,
   tad pamēģina `/feed/`, `/rss`, `/rss.xml` un vēl dažus.
3. **HTML scrape** (`scrape:`) - ja RSS nav vispār. Paņem ziņu lapu, savāc visas saites,
   kas atbilst `link_contains`, un patur tās, kuru teksts ir 25-250 zīmes garš
   (tas nogriež navigācijas pogas, bet atstāj virsrakstus).

Redzētie URL glabājas `seen.json`, ko workflow pats iekomitē atpakaļ repozitorijā.
Tāpēc dublikātu nav pat tad, ja lapa rakstus pārkārto.

**Filtrs.** Plašajiem portāliem (LSM, Delfi, TVNET, ministrijas) ir `filter: true` -
raksts iet cauri tikai tad, ja virsrakstā vai kopsavilkumā ir kāds no
`keywords` sarakstā esošajiem vārdiem. Nozares medijiem filtra nav, jo tur viss
ir par tēmu. Filtrs salīdzina bez diakritikas, tāpēc `buvniec` ķer arī `Būvniecība`.

## Lokālā palaišana

Ja kādreiz gribēsi testēt uz sava datora (nav obligāti):

```bash
pip install -r requirements.txt
python monitor.py --only building --dry-run   # viens avots, neko nesūta
python discover.py                            # pilna pārbaude -> discover-report.md
```

## Ko šis NEDARA

- Nelasa maksas sienas aiz esošo rakstu saturu (db.lv, Ir) - dabūsi virsrakstu un saiti.
- Nevērtē, vai raksts ir svarīgs. Tas ir tavs darbs.
- Nesūta drukāto žurnālu (Latvijas Architektūra, Latvijas Būvniecība) saturu - tie
  tiešsaistē neiznāk.
