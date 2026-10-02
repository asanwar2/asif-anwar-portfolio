# OpenMC setup — complete beginner walkthrough

Follow this top to bottom. Do not skip ahead. Each step has a check;
if the check fails, stop and fix it before continuing.

Total time: about 90 minutes, most of it downloads.
Disk space needed: about 15 GB free.

---

# PART 0 — Understand what you're about to do

OpenMC has no Windows version. So you will install **Ubuntu Linux inside
Windows** using a Microsoft feature called WSL (Windows Subsystem for Linux).
It is not a virtual machine you have to manage, it is not dual-booting, and
it will not touch your Windows files. It just adds a Linux terminal.

From then on there are **two separate worlds on your laptop**:

| | Windows side | Linux side |
|---|---|---|
| Terminal | Command Prompt / PowerShell | Ubuntu |
| Your files | `C:\Users\YourName\` | `/home/yourname/` |
| Where OpenMC lives | nowhere | here |

**Rule for the rest of this document: every command goes in the Ubuntu
terminal unless I explicitly say PowerShell.** Running conda in Command
Prompt is the #1 way beginners waste an afternoon.

Mac users: skip to PART 8 at the bottom. Your setup is much shorter.

---

# PART 1 — Install WSL (Ubuntu)

### 1.1 Check your Windows version

Press `Windows key + R`, type `winver`, press Enter.

You need Windows 11, or Windows 10 version 2004 or higher. If you're on
something older, update Windows first.

### 1.2 Open PowerShell as Administrator

- Press the Windows key
- Type `powershell`
- **Right-click** "Windows PowerShell" → **Run as administrator**
- Click Yes on the popup

You should see a blue window with a prompt ending in `>`.

### 1.3 Install WSL

Type this exactly and press Enter:

```powershell
wsl --install
```

This downloads and installs Ubuntu. It takes several minutes.

### 1.4 Restart your computer

Actually restart. Not sleep, not sign out. Restart.

### 1.5 Finish Ubuntu setup

After restarting, a black terminal window may open by itself. If it doesn't:
press the Windows key, type `Ubuntu`, press Enter.

It will say it's installing, then ask you to create a username and password.

- **Username:** lowercase, no spaces. Something like `asif`.
- **Password:** you will NOT see anything as you type — no dots, no stars.
  That's normal Linux behavior, not a broken keyboard. Type it, press Enter,
  type it again, press Enter.
- Write this password down. You'll need it for `sudo` commands.

### ✅ CHECK 1

Your prompt should now look something like:

```
asif@LAPTOP-1234:~$
```

That `$` at the end means you're in Linux. If you see `C:\Users\...>` you're
still in Windows — close it and open Ubuntu from the Start menu.

**From here on, "the terminal" means this Ubuntu window.**

---

# PART 2 — Update Ubuntu

Run these two commands, one at a time:

```bash
sudo apt update
```

It will ask for the password you just made. Type it (again, invisible) and
press Enter.

```bash
sudo apt upgrade -y
```

This takes a few minutes. Let it finish.

Then install two small tools you'll need:

```bash
sudo apt install -y wget tar
```

### ✅ CHECK 2

```bash
wget --version
```

Should print a version number, not "command not found."

---

# PART 3 — Install conda (Miniforge)

Conda is a package manager. Miniforge is the version pre-configured for
conda-forge, which is where OpenMC lives. Don't use Anaconda — it's bloated
and its default channel will fight you.

### 3.1 Download the installer

```bash
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
```

### 3.2 Run it

```bash
bash Miniforge3-Linux-x86_64.sh
```

Then:
- Press Enter to read the license, then hold Enter or press `q` to get out
- Type `yes` and press Enter to accept
- Press Enter to accept the default install location
- When it asks whether to run `conda init` — type `yes` and press Enter

### 3.3 Restart your terminal

Close the Ubuntu window entirely. Open it again from the Start menu.

### ✅ CHECK 3

Your prompt should now start with `(base)`:

```
(base) asif@LAPTOP-1234:~$
```

If it doesn't, run `source ~/.bashrc` and check again.

---

# PART 4 — Install OpenMC

### 4.1 Create an environment and install

```bash
conda create --name openmc-env openmc
```

Type `y` when it asks to proceed. This downloads several hundred MB and takes
5–15 minutes. It will look frozen at "Solving environment" — it isn't.

### 4.2 Activate it

```bash
conda activate openmc-env
```

Your prompt changes from `(base)` to `(openmc-env)`.

**You must run `conda activate openmc-env` every time you open a new
terminal.** Forgetting this is the second most common beginner problem.

### ✅ CHECK 4

Run both of these:

```bash
python -c "import openmc; print(openmc.__version__)"
openmc --version
```

Both must print a version number. If the first works and the second says
"command not found," something went wrong — delete the environment
(`conda env remove -n openmc-env`) and redo step 4.1.

---

# PART 5 — Nuclear data (the step that stops people)

OpenMC ships with no cross-section data. Without it, nothing runs.

### 5.1 Download it (do this part in Windows)

Open your normal Windows browser and go to:

**https://openmc.org/official-data-libraries/**

Download the **ENDF/B-VIII.0** library. It's roughly 2 GB. Let it save to
your normal Downloads folder.

### 5.2 Find it from Linux

Your Windows C: drive is visible from Ubuntu at `/mnt/c/`. So:

```bash
ls /mnt/c/Users/
```

Find your Windows username in that list, then:

```bash
ls /mnt/c/Users/YOUR_WINDOWS_NAME/Downloads/
```

Replace `YOUR_WINDOWS_NAME` with what you saw. You should see the downloaded
file — something like `endfb-viii.0-hdf5.tar.xz`.

### 5.3 Copy it into Linux and unpack

```bash
cd ~
mkdir nuclear_data
cd nuclear_data
cp /mnt/c/Users/YOUR_WINDOWS_NAME/Downloads/endfb-viii.0-hdf5.tar.xz .
tar -xf endfb-viii.0-hdf5.tar.xz
```

The `tar` step takes several minutes and prints nothing. That's fine.

### 5.4 Find the cross_sections.xml file

```bash
find ~/nuclear_data -name "cross_sections.xml"
```

Copy the full path it prints. It'll look something like:

```
/home/asif/nuclear_data/endfb-viii.0-hdf5/cross_sections.xml
```

### 5.5 Tell OpenMC where it is — permanently

```bash
echo 'export OPENMC_CROSS_SECTIONS=/home/asif/nuclear_data/endfb-viii.0-hdf5/cross_sections.xml' >> ~/.bashrc
source ~/.bashrc
```

**Replace that path with the one YOU got from step 5.4.** Do not copy mine.

### ✅ CHECK 5

```bash
conda activate openmc-env
python -c "import openmc; print(openmc.config['cross_sections'])"
```

This must print your path. If it errors or prints nothing, OpenMC can't find
the data and no simulation will run.

---

# PART 6 — Set up VS Code (this is where your editor comes in)

### 6.1 Install VS Code on Windows

If you don't have it: https://code.visualstudio.com/ — install normally, on
the Windows side.

Note: VS Code and Visual Studio are different programs. You want **VS Code**.

### 6.2 Install the WSL extension

Open VS Code. Click the Extensions icon in the left sidebar (four squares).
Search for **WSL** (publisher: Microsoft). Click Install.

### 6.3 Make a project folder and open it

Back in your Ubuntu terminal:

```bash
cd ~
mkdir aneel-openmc
cd aneel-openmc
code .
```

The first time you run `code .` it installs a small server component, then
VS Code opens. Look at the **bottom-left corner** — it should say something
like `WSL: Ubuntu`. That means VS Code is editing Linux files, which is what
you want.

### 6.4 Use the terminal inside VS Code from now on

In VS Code: menu **Terminal → New Terminal**. It opens an Ubuntu shell
already in your project folder. Run `conda activate openmc-env` in it and
you can edit and run from one window.

---

# PART 7 — Get the scripts in and run the first one

### 7.1 Copy the scripts over

Download the four `.py` files and `00_SETUP.md` to your Windows Downloads,
then in the Ubuntu terminal:

```bash
cd ~/aneel-openmc
cp /mnt/c/Users/YOUR_WINDOWS_NAME/Downloads/0*.py .
ls
```

You should see all four files listed.

(Alternative: in VS Code, File → New File, paste the contents, save with the
right name. Works fine too.)

### 7.2 Run the first one

```bash
conda activate openmc-env
python 01_pincell.py
```

### ✅ CHECK 6 — the real one

You'll see a wall of output. At the bottom, look for a k-inf value printed
between two rows of `=` signs.

**If you got a number, you're done setting up.** Everything from here is
physics, and physics you already know.

### If it failed, read the error

| Error contains | Meaning | Fix |
|---|---|---|
| `ModuleNotFoundError: openmc` | environment not active | `conda activate openmc-env` |
| `Cannot find cross_sections.xml` | data path wrong | redo Part 5.5 |
| `No cross section data available for Th232` | wrong/partial library | make sure you got ENDF/B-VIII.0, not a small test library |
| `command not found: openmc` | broken install | redo Part 4 |
| `No such file or directory: 01_pincell.py` | wrong folder | `cd ~/aneel-openmc` then `ls` |

---

# PART 8 — Mac instructions (skip if on Windows)

No WSL needed. Open the **Terminal** app (Cmd+Space, type "Terminal").

```bash
# Install Miniforge
curl -L -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh
bash Miniforge3-$(uname)-$(uname -m).sh
```

Close and reopen Terminal, then:

```bash
# Apple Silicon (M1/M2/M3/M4) needs the x86 platform flag:
conda create --name openmc-env --platform osx-64 openmc

# Intel Mac:
conda create --name openmc-env openmc

conda activate openmc-env
```

Then follow **Part 5** for nuclear data, using `~/Downloads/` instead of
`/mnt/c/Users/.../Downloads/`, and add the export line to `~/.zshrc` instead
of `~/.bashrc`.

VS Code works directly — no WSL extension needed.

---

# Daily routine, once set up

Every time you sit down to work:

```bash
conda activate openmc-env
cd ~/aneel-openmc
```

That's it. Two commands.

---

# Things worth knowing that will confuse you later

- **Linux is case-sensitive.** `Fuel.py` and `fuel.py` are different files.
- **`~` means your home folder** (`/home/asif`).
- **Tab completion works.** Type `pyt` then press Tab. Use it constantly.
- **Ctrl+C stops a running program.** You will need this when a simulation
  is taking longer than you expected.
- **Copying in the terminal:** Ctrl+Shift+C to copy, Ctrl+Shift+V to paste.
  Plain Ctrl+C kills the program instead.
- Files you create in `~/aneel-openmc` are NOT in your Windows folders. To
  see them from Windows, open File Explorer and type `\\wsl$` in the address
  bar.
