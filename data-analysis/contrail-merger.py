import glob, cv2
import numpy as np

contrail_file_list = glob.glob("*.jpg")
contrail_dict = {}

for contrail in contrail_file_list:
    filename = contrail[:-4]
    animalID, timepoint, treatment, trial = filename.split("_")
    trial_num = int(trial[-1:])
    try:
        contrail_dict[animalID]
    except:
        contrail_dict[animalID] = []
    contrail_dict[animalID].append(contrail)

color = [ [75, 25, 230], [48, 130, 245], [25, 225, 255], [60, 245, 210], [75, 180, 60], [240, 240, 70], [200, 130, 0], [180, 30, 145], [230, 50, 240], [128, 128, 128] ]

for animal in contrail_dict:
    
    count = 0
    merge_image = np.zeros((480,640,3), np.uint8)
    
    for file in contrail_dict[animal]:
        animal_color = color[count]
        img = cv2.imread(file, cv2.IMREAD_COLOR)
        img[np.where((img > [200,200,200]).all(axis = 2))] = animal_color
        merge_image = cv2.add(merge_image, img)
        cv2.imshow(file , merge_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        filenameZ = file[:-4]
        animalIDZ, timepointZ, treatmentZ, trialZ = filenameZ.split("_")
        trial_numZ = int(trial[-1:])
        count += 1
    cv2.imwrite(animalIDZ + '_' + timepointZ + '_' + treatmentZ + '.jpg', merge_image)
    