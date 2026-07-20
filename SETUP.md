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

## Refresh profile artwork locally

The profile uses a regular portrait in a terminal-style PNG panel. To regenerate the panel, information card, and heatmap:

```powershell
python scripts/make_portrait_panel.py
python scripts/make_info_card.py
python scripts/render_heatmap_svg.py
```

## Replacing your portrait

Replace `assets/marcel-portrait.png` with a clean, head-and-shoulders photo. PNG works best, but you may use a JPEG if you also update the source path in `scripts/make_portrait_panel.py`. Then rebuild the framed panel:

```powershell
python scripts/make_portrait_panel.py
```

The script uses a centred crop and never stretches the source image. The generated `assets/marcel-portrait-panel.png` is the GitHub-safe terminal frame used by the README.
