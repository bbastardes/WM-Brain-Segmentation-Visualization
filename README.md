# WM-Brain-Segmentation-Visualization

The aim of this project is to implement and develop a visualization tool to help the analysis of the white matter tracts of the brain.

The dataset used for this project is composed by T1 weighted images, diffusion weighted images (DWI) and masks of tracts from the white matter of the human brain. The structural and diffusion images come from the Human Connectome Project database [1] and the masks come from a paper from Wasserthal, Neher, and Maier-Hein [2].

The only preprocessing done was with the DWI images. They were converted to tensors in order to be able to implement the glyph representation in the application. The rest of the computations are implicitly done in the background when using the tool.

The are three main functionalities of the tool proposed:

- 3D Visualization: The T1w image is selected by the user and therefore the T1 will be displayed in its corresponding frame. There will be a box with all the masks available so that the user can enable or disable them in order to be displayed with the T1 in the same frame.

- 2D Visualization: The T1 previously loaded and the masks of interest selected will be displayed in 2D in three different frames corresponding to the axial, sagittal and coronal views.

- Glyph representation: The user will load a file with the tensors and select which are the tracts to explore their intersection (crossing region). This intersection will be computed in the background and a glyph representa- tion of the direction of the diffusion will be displayed. A fusion of the T1 and the masks of the tracts being intersected will be displayed as well.

[1] WU-Minn Consortium Human Connectome Project. “WU-Minn HCP 500 Subjects Data Release: Reference Manual”. In: Proceedings of OHBM An- nual Meeting (2014).

[2] J. Wasserthal, P. Neher, and K. Maier-Hein. “TractSeg - Fast and accurate white matter tract segmentation”. In: NeuroImage 183 (2018), pp. 239–253.
