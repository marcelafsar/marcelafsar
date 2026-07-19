# Install the profile README

This folder is ready to copy into the public `marcelafsar/marcelafsar` profile repository.

## Recommended Windows steps

1. Download and extract the ZIP.
2. Open PowerShell inside your local `marcelafsar` profile repository.
3. Copy the contents of the extracted folder into the repository root. The root should contain:

   - `README.md`
   - `assets/`
   - `data/`
   - `scripts/`
   - `.github/workflows/update-profile-art.yml`

4. Review the new profile locally by opening `preview.html` in a browser.
5. Commit and push:

```powershell
git add README.md assets data scripts .github
git commit -m "feat: redesign GitHub profile"
git push origin main
```

6. On GitHub, open the profile repository and go to **Actions**.
7. Open **Update profile activity**, choose **Run workflow**, and run it once.
8. The workflow will fetch the live contribution calendar, regenerate `assets/contrib-heatmap.svg`, and commit the result automatically.

## If the workflow cannot push

Open the repository's **Settings → Actions → General → Workflow permissions**, select **Read and write permissions**, save, and run the workflow again.

## Rebuild the static animations locally

The animated ASCII portrait and neofetch card are already generated. To regenerate them after editing their source data:

```powershell
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
python scripts/render_heatmap_svg.py
```

Set `STATIC=1` before generating an SVG when you need a non-animated preview frame.

```powershell
$env:STATIC="1"
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
Remove-Item Env:STATIC
```

## Customizing the ASCII scene

Edit `data/ascii_scene.txt`, then run:

```powershell
python scripts/make_ascii_svg.py
```

Each text row is revealed left-to-right and staggered from top to bottom. The animation runs once and freezes.
