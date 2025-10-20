<details>
  <summary>Project Development Roadmap</summary>

---
# Project Development Roadmap
<details>
  <summary>🚀 Phase 1 — χD Calculator (Q1 2025)</summary>
 

 **Goal:** Convert structural data (SDF file) into diamagnetic susceptibility.
 

**Tasks:**
  -  Create Pascal's constants dictionary
  -  Write basic introduction and usage examples   
  -  Connect RDKit library with the dictionary  
  -  Implement testing and error handling  
  -  Develop user-friendly frontend interface  

---
</details>

<details>
  <summary>🔬 Phase 2 — DC Magnetic Data Tool (Q2 2026)</summary>


**Goal:** Develop a module for processing and visualizing DC magnetic data.


**Tasks:**
  -  Create standard input format for magnetic data  
  -  Develop core data-processing functions  
  -  Implement testing and error handling  
  -  Build frontend and visualization components

---
</details>

 <details>
  <summary>📦🔬Phase 3 — AC Magnetic Data Tool (Q3 2026)</summary>


**Goal:** Develop a module for analyzing and visualizing AC magnetic susceptibility data.

**Tasks:**
  -  Create standard input format for magnetic data
  -  Develop core data-processing functions
  -  Implement testing and error handling
  -  Build frontend and visualization components

---
</details>


<details>
  <summary>💻 Phase 4 — Desktop Application & Local Software (Q4 2026)</summary>


**Goal:** Develop a cross-platform desktop application that integrates χD, DC, and AC magnetic data tools, providing a user-friendly interface for data input, processing, visualization, and export.


**Tasks:**
- [ ] Connect χD, DC, and AC modules.  
- [ ] Implement GUI for seamless workflow (data input → processing → results visualization)  
- [ ] Add robust testing, error handling, and validation for desktop use  
- [ ] Prepare installers for Windows, macOS, and Linux  
- [ ] Write comprehensive user documentation and usage examples  
- [ ] Optional: Add export features (CSV, PDF, plots) and advanced visualization tools  

---
</details>

---
</details>


<details>
  <summary>Git instructions</summary>


# Git Instructions

## Definitions
- **Repository (repo):** a project folder tracked by Git (can be local on your computer or remote on GitHub/GitLab).  
- **Commit:** a snapshot of your changes with a message describing what was done.  
- **Push:** upload your local commits to the remote repository.  
- **Pull:** download and merge the latest changes from the remote repository to your local copy.  
- **Staging (git add):** selecting which files/changes will go into the next commit.  

---
# Create Python Virtual Environment (only once at project start)
> [!IMPORTANT]
> Must know, allows to isolate projects' dependencies
```
python -m venv .venv
```
## Install requirements
> [!IMPORTANT]
> Make sure that `which python` command returns the venv path, restart the terminal to load venv
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```
# Git Instructions
# How to push local changes to repository?
## 1. how to fix merge conflicts
### 1.1 make sure your branch is up to date
> [!NOTE]
> you should have all files commited
```bash
git checkout <YOUR_BRANCH>
git status
```
### 1.2 be sure that local master is up to date
> [!NOTE]
> make sure master is clean and up to date with remote
```bash
git checkout master
git pull
```
### 1.3 go back to your branch
> [!NOTE]
> we are going to merge master into `<YOUR_BRANCH>`
```bash
git checkout <YOUR_BRANCH>
git status
```
### 1.4 merge master
> [!NOTE]
> be sure you are on your branch (master -> `<YOUR_BRANCH>`)
```bash
git merge master
git commit -m 'updated from master'
```
### 1.5 conflict after merge 
> [!IMPORTANT]
> in each file the conflict must be solved

**EXAMPLE:**
```bash
If you have questions, please
 <<<<<<< HEAD
open an issue
=======
ask your question in IRC.
 >>>>>>> branch-a
```
### 1.6 make a decision
> [!NOTE]
> choose version.
### 1.7 add version to change
> [!NOTE]
> solve in VS Code merge editor
```bash
git add .
git commit -m 'message'
```

## 2. add files to commit
```bash
git add --all
```

## 3. create commit with added files (staged files)
```bash
git commit -m 'what was changed? what is the new feature name?'
```

## 4. push changes (push commit)
```bash
git push
```

# How to pull changes (commits) from repository to local workstation?
```bash
git pull
```

# Git Branches
### 1. check available branches
```
git branch
```
### 2. Change branch
```
git checkout <BRANCH_NAME>
```
### 3. Create new branch
```
git checkout -b <BRANCH_NAME>
```

### 4. Push branch **for the first time**
```
git push -u origin <BRANCH_NAME>
```

### 5. Delete local branch
```
git branch --delete <BRANCH_NAME>
```

# How to see flags documentation
>  Use arrows to go up / down if using vim, press "q" to exit, or search in google `git push manual` or `git pull documentation`
```
git push --help
git pull --help
git --help
```

# Dictionaries
## 1. Standard `dict` functions
> These are useful function for working with dictionaries. They are **especially useful** when working with `for each` loops:
 - `.keys()`, `.values()`, `.items()`
 - `.get()`
```python
mydict: dict = {
  'some_key': 'some value',
  'another_key': 0.1,
  'yet_another_key': ['yet', 'another', 'value'],
  }
```

## 1.1 **Most common loop** - iterate over every `key, value` using `.items()`
> [!IMPORTANT]
> Must know
```python
for key, value in mydict.items():
  print(f'key: "{key}" -> value: "{value}"')
```
- Log Output:
```
key: "some_key" -> value: "some value"
key: "another_key" -> value: "0.1"
key: "yet_another_key" -> value: "['yet', 'another', 'value']"
```

## 1.2 Check if `key` exists in a `dict`
> [!IMPORTANT]
> Must know, below examples evaluate the same
```python
if 'some_key' in mydict.keys(): # EXPLICIT call
  print('key exists')

if 'some_key' in mydict:        # IMPLICIT call - "hidden default call"
  print('key exists')
```

## 1.3 Setting defaults: `.get()`
> [!IMPORTANT]
> Must know
```python
x = mydict.get('i_dont_exist', 'default value')
y = mydict.get('some_key', 'default value')
print(f'x is: "{x}", y is: "{y}"')
```
- Log Output:
```
x is: "default value", y is: "some value"
```
### 1.3.1 `.get()` use case
> [!IMPORTANT]
> Must know, below examples evaluate the same
```python
if symbol in ox_state_data.keys():  # not optimal
  sum_dia_contr += ox_state_data[symbol] * atoms

sum_dia_contr += ox_state_data.get(symbol, 0) * atoms # optimal
```

## 1.4 Loop over keys using `.keys()`
> [!NOTE]  
> Useful to know
```python
for key in mydict.keys():
    value = mydict[key] # you still can get the value
    print(f'key: "{key}" -> value: "{value}"')
```
- Log Output:
```
key: "some_key" -> value: "some value"
key: "another_key" -> value: "0.1"
key: "yet_another_key" -> value: "['yet', 'another', 'value']"
```

## 1.5 Loop over values using `.values()`
> [!NOTE]  
> Rarely used. Only when `key` is not needed
```python
for value in mydict.values():
    print(f'value: "{value}"')
```
- Log Output:
```
value: "some value"
value: "0.1"
value: "['yet', 'another', 'value']"
```

</details>
