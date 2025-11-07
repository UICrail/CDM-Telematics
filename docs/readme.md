The Wiki contents can be packed into a markdown by a script, then transformed using Pandoc. The action can be triggered manually (see "Actions" menu). It is triggered automatically:
* When a wiki page gets created, updated, or deleted
* When an image in /Graphol/diagrams/ gets created, updated, or deleted

The output consists of following files:
* A standalone markdown file with embedded images: please disregard, as some images are not properly "inserted" and displayed.
* A standalone markdown file with images in a subfolder: can be viewed in Typora, but trouble with Obsidian and with the GitHub renderer.
* A LaTeX file with images in the subfolder: cannot be viewed in GitHub (which has no LaTeX extensions), but TexStudio (a free, multi-platform desktop editor) compiles and displays it. Also works with VScode LaTeX extensions, or with Overleaf (online).
* A pdf file with embedded images: works in every environment we could test.

The file generation may take up to three minutes.

Important: **the authoritative source is the Wiki**, and the transformation is one-way!
