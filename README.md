# 🌊 AVATAR: The Game Water Editor

![GitHub release (latest by date)](https://img.shields.io/github/v/release/JasperZebra/AVATAR-The-Game-Water-Editor?style=for-the-badge&logo=github&color=00ffff&logoColor=white&labelColor=1a4d66)
![Total Downloads](https://img.shields.io/github/downloads/JasperZebra/AVATAR-The-Game-Water-Editor/total?style=for-the-badge&logo=github&color=00ffff&logoColor=white&labelColor=1a4d66) 
![Platform](https://img.shields.io/badge/platform-windows-00ffff?style=for-the-badge&logo=windows&logoColor=00ffff&labelColor=1a4d66)
![Made for](https://img.shields.io/badge/made%20for-2009_AVATAR:_The_Game-00ffff?style=for-the-badge&logo=gamepad&logoColor=00ffff&labelColor=1a4d66) 
![Tool Type](https://img.shields.io/badge/type-water%20editor-00ffff?style=for-the-badge&logo=droplet&logoColor=00ffff&labelColor=1a4d66)

A tool for adding and managing water blocks in `.csdat` sector files. Perfect for game modders and level designers working with sector-based terrain systems.

## ✨ Features

- **🗺️ Visual Sector Grid** - Interactive 16×16 sector map showing water placement at a glance
- **💧 Precise Water Height Control** - Adjust water levels with slider or direct numeric input (0-50 range)
- **🎨 Multiple Water Materials** - Choose from 6 pre-configured water types:
  - Default water top
  - Open field water
  - Rainforest water
  - Rainforest water (no reflection)
  - Riverbank water
  - Swamp water
- **⚡ One-Click Operations** - Add, save, or reset water blocks with simple button clicks
- **🎯 Real-time Preview** - See which sectors contain water instantly on the grid
- **🔒 Safe Editing** - Preserves original sector data while modifying water parameters
- **🎨 Modern Dark UI** - Clean, professional interface with color-coded sector states

## 📸 Screenshot

<img width="1204" height="752" alt="image" src="https://github.com/user-attachments/assets/3275fd72-2780-45da-b8b6-9fab8fb6579d" />

## 📖 How to Use

### Basic Workflow

1. **Load SDAT Folder**
   - Click "📁 Load SDAT Folder"
   - Select the folder containing your sector files (sd0.csdat, sd1.csdat, etc.)

2. **Select a Sector**
   - Click any cell in the 16×16 grid to select a sector
   - Selected sector appears in red
   - Blue sectors already contain water

3. **Add Water Block** (First Time Setup)
   - Click "➕ Add Water Block" to initialize the water system for the selected sector
   - This copies the water template into the sector file

4. **Configure Water**
   - Adjust **Water Height** using the slider or text input (0.00 - 50.00)
   - Choose **Water Material** from the dropdown menu

5. **Save Changes**
   - Click "💾 Save Sector" to apply your changes
   - The sector will turn blue on the grid

6. **Reset (Optional)**
   - Click "🔄 Reset Sector" to remove water and clears all water data

### Grid Legend
- **Gray** - Empty sector (no water)
- **Blue** - Sector contains water
- **Red** - Currently selected sector

## ⚠️ Important Notes

- **Backup Your Files**: Always keep backups of your original SDAT files before editing
