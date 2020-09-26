import vtk
import numpy as np
import nibabel as nib

# compute intersection of two masks
def Intersection(mask1,mask2):
    
    print(mask1)
    print(mask2)

    # load mask1
    img = nib.load(mask1+'.nii.gz')
    mask1_img = img.get_data()
    
    # binarize prob masks
    # in case we have probability masks
    #mask1_img = (mask1_img > 0).astype(int)

    # load mask2
    img2 = nib.load(mask2+'.nii.gz')
    mask2_img = img2.get_data()
    
    # mask2_img = (mask2_img > 0).astype(int)

    intersec = mask1_img * mask2_img

    intersec_img = nib.Nifti1Image(intersec.astype(int), img2.affine)
    nib.save(intersec_img, 'intersec_img.nii.gz')

    return intersec
