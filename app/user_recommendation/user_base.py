import pandas as pd
from difflib import SequenceMatcher

from fastapi import APIRouter, HTTPException, status

from .filter import final_df, filter_7

from . import schemas

router = APIRouter(
    prefix="/User-Based",
    tags=['User_Collaborative_Filter']
)    


@router.post("/recommendation by User's Data")
# getting the product name from the user
def recommend(request: schemas.ProjectDetails):
    
    # conversion of key to name
    try:
        project_name = filter_7.at[filter_7.index[filter_7['projectcode'] == request.projectcode][0], 'projectname']
    except Exception as e:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"projectcode : '{request.projectcode}' dosen't had any key value")
        
    try:
        system_name = filter_7.at[filter_7.index[filter_7['systemnamekey'] == request.systemnamekey][0], 'systemname']
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"systemnamekey : '{request.systemnamekey}' dosen't had any key value")
        
    try:    
        component_name = filter_7.at[filter_7.index[filter_7['componentnamekey'] == request.componentnamekey][0], 'componentname']
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"componentnamekey : '{request.componentnamekey}' dosen't had any key value")
    
    # filter a table with user input project_name and system_name.
    select_by_project = final_df[final_df['mainproject'] == project_name]
    if not select_by_project.any().any():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project_id : {project_name} is not available")
        
    
    select_by_systemname = select_by_project[select_by_project['systemname'] == system_name]
    if not select_by_systemname.any().any():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"System_name_key : {system_name} is not available")
    similarity_scores = []

    # give score to componentname column by input-data.
    column = select_by_systemname['componentname']
    for element in column:
        similarity = SequenceMatcher(None, component_name, element).ratio()
        similarity_scores.append(similarity)
    select_by_systemname['similarity_scores'] = similarity_scores


    # filtering the table with similarity_scores column that contains our score requirement.
    score = 0.7
    select_by_score = select_by_systemname[select_by_systemname['similarity_scores'] >= score]
    print(f'similarity_scores column that contains more then {score} :')
    print(select_by_score)
    if not select_by_score.any().any():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Similar Componentnamekey for '{component_name}' is not available")

    # create a new column 'repeated_counts' and insert a repeated count of the projectname.
    value = select_by_score.groupby('projectname').size().reset_index(name='repeated_counts')
    repeated_result = select_by_score.merge(value, on='projectname', how='left')


    # find the maximum repeated_count value.
    column = repeated_result['repeated_counts']
    max_repeated_value = column.max()


    # iterate the value maximum to minimum
    list_1 = []
    r = max_repeated_value
   
    for a in range(r, 0, -1):
        # print(f'{a} no of users are compared with this part')
        table = repeated_result[repeated_result['repeated_counts'] == a]
        #     print(table)
        for b in range(len(table)):
            projectname1 = table.iloc[b]['projectname']
            systemname1 = table.iloc[b]['systemname']
            componentname1 = table.iloc[b]['componentname']
            dic1 = {"projectname": projectname1, "systemname": systemname1, "componentname": componentname1}
            list_1.append(dic1)
        break
    final_result = list_1

    # view the result dictionary in table formate.
    output = pd.DataFrame(final_result)
    print('Most users compared projects : ')
    print(output)
    return {"result": final_result}












