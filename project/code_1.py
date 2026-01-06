import pandas as pd

def my_function():
    # Create a DataFrame with numeric values
    df = pd.DataFrame({
        "leandro": [2],  # Add square brackets to create a list
        "isabella": [3],
        "thiago": [4],
        "marlea": [2040]
    })

    # Specify the output file path (adjust as needed)
    output_path = r'C:\Users\Cliente\Desktop\data_1.xlsx'

    # Save the DataFrame to an Excel file
    df.to_excel(output_path, index=False)

# Call your function here
my_function()