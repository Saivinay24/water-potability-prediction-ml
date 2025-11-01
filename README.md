# Water Potability Prediction using Machine Learning

This is a Data Processing and Visualization (DPV) project that aims to solve a critical global challenge: ensuring access to safe drinking water.

The project trains and evaluates machine learning models to classify water samples as "Potable" (safe to drink) or "Not Potable" (unsafe) based on their chemical features.

## Project Pipeline

1.  **Data Source:** The project uses the standard "Water Potability" dataset from Kaggle.
2.  **Preprocessing:** A key challenge in this dataset is missing data. As a baseline, missing values in the `ph`, `Sulfate`, and `Trihalomethanes` columns were imputed using the mean of each column.
3.  **Exploratory Data Analysis (EDA):**
    * **Class Distribution:** A count plot revealed a critical insight: the dataset is **imbalanced**, with more "Not Potable" (Class 0) samples than "Potable" (Class 1) samples.
    * **Correlations:** A heatmap was generated to analyze the relationships between features.
    * **Distributions:** Histograms were used to visualize the statistical distribution of all chemical features.
4.  **Model Training & Evaluation:**
    * The data was split (80% train, 20% test) and standardized using `StandardScaler`.
    * Three baseline models were trained and compared:
        1.  Logistic Regression
        2.  K-Nearest Neighbors (KNN)
        3.  Random Forest
    * Models were evaluated using 5-fold cross-validation and a final test set classification report.

## Results & Key Finding

While the Random Forest model achieved the highest baseline accuracy of **68.1%**, this metric was misleading.

The classification report and confusion matrix revealed that the model was heavily biased by the imbalanced data. It was excellent at identifying "Not Potable" water (Class 0) but extremely poor at identifying "Potable" water (Class 1), with a recall of only **0.38**. This means it failed to identify 62% of all safe drinking water samples.

| Model | Cross-Val Score | Test Accuracy | Test Recall (Class 1) |
| :--- | :---: | :---: | :---: |
| Logistic Regression | 60.53% | 62.8% | **0.00** |
| K-Nearest Neighbors | 62.75% | 62.8% | 0.42 |
| **Random Forest** | **66.68%** | **68.1%** | **0.38** |

## Conclusion & Future Work

The primary conclusion of this phase is that baseline accuracy is not a useful metric for this problem. The model's failure to identify the minority "Potable" class makes it unusable in its current state.

This finding aligns with existing academic literature. The clear next step, as proposed in the project's "Phase 2," is to address this class imbalance by applying the **SMOTE (Synthetic Minority Over-sampling Technique)** to the training data to create a balanced dataset. Retraining the models on this balanced data is expected to significantly improve the recall for Class 1 and create a truly effective predictive tool.

## How to Run

All analysis is contained within the `Dpv_lab.ipynb` notebook.
Key libraries used:
* `pandas`
* `matplotlib`
* `seaborn`
* `scikit-learn` (for `train_test_split`, `StandardScaler`, `LogisticRegression`, `KNeighborsClassifier`, `RandomForestClassifier`, and `cross_val_score`)
