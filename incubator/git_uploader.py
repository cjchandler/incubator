import os
import time





#this has to run all the time, seperate the saving files from climate control since if internet goes down I want to be able to keep climate control on 




def  update_file_in_git_and_remove_all_git_history( path_original , target_path , file_name):
    os.system( "cd " + target_path)

    #COPY PATH file to current dir 
    os.system(  "cp " + path_original+file_name + " " + target_path+ file_name )

    #add and commit
    os.system( "git add .")
    os.system('git commit -a -m "data" ')

    #delete all previous commit history
    os.system( "git checkout --orphan newBranch")
    os.system( "git add -A  ")# Add all files and commit them
    os.system( "git commit -a  -m 'auto commit with git history delete to keep repo size small' ")
    os.system("git branch -D main  ")# Deletes the master branch
    os.system("git branch -m main  ")# Rename the current branch to master
    os.system("git push -f origin main  ")# Force push master branch to github
    os.system("git gc --aggressive --prune=all     ")# remove the old files

origpath = "/home/carl/Git_Projects/incubator_public/incubator/incubator/"
targetpath = "/home/carl/Git_Projects/incubator_daily/"
file_name = "today_dataV4.csv"
update_file_in_git_and_remove_all_git_history( origpath, targetpath, file_name)





while True:
    try: 
        os.system("git add . ")
        os.system("git commit -a -m  'auto update' ")
        os.system("git push origin main ")
    except: 
        print("git not pushing right")
        
    try: 
        update_file_in_git_and_remove_all_git_history()
    except:
        print("daily repo thing not working")
        
    time.sleep(60)
