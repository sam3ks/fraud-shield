## **SAMPLING STRATEGY**

### **Introduction**

This document outlines the sampling strategy used to determine the most
effective train-test split for fraud detection modeling. Given the large
size of the IEEE-CIS fraud detection dataset, we selected a subset of
10,000 rows to analyze the impact of different splits on model
performance. By evaluating multiple train-test ratios, we aim to
identify the best configuration for training and testing before applying
the approach to the full dataset.

### **Model Used for Evaluation**

All the above train-test splits were executed for **Model A (Balanced
Sampling, High Learning Rate)** to assess its performance under
different data distributions. This approach ensures that the evaluation
is consistent and provides insights into how the model adapts to varying
training and testing proportions.

### **Dataset Selection**

- A sample of 10,000 rows was taken from the IEEE-CIS fraud detection
  dataset.

### **Reason for Sampling**

- Since the dataset is very large, a smaller subset was chosen to
  efficiently evaluate different train-test splits before applying the
  approach to the full dataset.

### **Train-Test Splits Tested**

- Various train-test splits were analyzed, including **70-30, 55-45,
  75-25, 65-35, 80-20, and 50-50**.

### 

### **Evaluation Approach**

- Classification reports for each split are presented below to provide a
  detailed comparison and assess their impact on model performance.

1.  70-30 split:

|              | Precision | recall | F1-score | support |
|--------------|-----------|--------|----------|---------|
| 0            | 0.91      | 0.92   | 0.91     | 1400    |
| 1            | 0.81      | 0.8    | 0.81     | 600     |
| accuracy     |           |        | 0.88     | 0.88    |
| Marco avg    | 0.86      | 0.86   | 0.86     | 2000    |
| Weighted avg | 0.88      | 0.88   | 0.88     | 2000    |

**70-30 Split:** This split provides a balanced performance with an
overall accuracy of 88%, maintaining a strong F1-score across both
classes. It ensures that the model has sufficient data for training
while preserving a reasonable test set for evaluation.

2.  55-45 split:

|              | Precision | recall | F1-score | support |
|--------------|-----------|--------|----------|---------|
| 0            | 0.85      | 0.85   | 0.85     | 900     |
| 1            | 0.88      | 0.88   | 0.88     | 1100    |
| accuracy     |           |        | 0.87     | 2000    |
| Marco avg    | 0.86      | 0.86   | 0.86     | 2000    |
| Weighted avg | 0.87      | 0.87   | 0.87     | 2000    |

**55-45 Split:** The accuracy of 87% in this split shows a slightly
lower performance than 70-30, with class 1 (fraudulent transactions)
achieving a better recall. However, the overall balance between classes
is not as optimal as in the 70-30 split.

3.  75-25 split:

|              | Precision | recall | F1-score | support |
|--------------|-----------|--------|----------|---------|
| 0            | 0.92      | 0.92   | 0.92     | 1500    |
| 1            | 0.76      | 0.77   | 0.76     | 500     |
| accuracy     |           |        | 0.88     | 2000    |
| Marco avg    | 0.84      | 0.84   | 0.84     | 2000    |
| Weighted avg | 0.88      | 0.88   | 0.88     | 2000    |

**75-25 Split:** With an accuracy of 88%, this split performs similarly
to 70-30 but shows a lower F1-score for fraudulent transactions (0.76),
which may impact fraud detection. The slightly reduced test size could
also affect model validation.

4.  65-35 split

|              | Precision | recall | F1-score | support |
|--------------|-----------|--------|----------|---------|
| 0            | 0.92      | 0.9    | 0.91     | 1300    |
| 1            | 0.82      | 0.85   | 0.83     | 700     |
| accuracy     |           |        | 0.88     | 2000    |
| Marco avg    | 0.87      | 0.87   | 0.87     | 2000    |
| Weighted avg | 0.88      | 0.88   | 0.88     | 2000    |

**65-35 Split:** Achieving 88% accuracy, this split maintains a good
balance between precision and recall. The recall for fraudulent
transactions (0.85) is higher than in some other splits, making it a
viable option, though it does not significantly outperform 70-30.

5.  80-20 split:

|              | Precision | recall | F1-score | support |
|--------------|-----------|--------|----------|---------|
| 0            | 0.93      | 0.95   | 0.94     | 1600    |
| 1            | 0.79      | 0.69   | 0.74     | 400     |
| accuracy     |           |        | 0.9      | 2000    |
| Marco avg    | 0.86      | 0.82   | 0.84     | 2000    |
| Weighted avg | 0.9       | 0.9    | 0.9      | 2000    |

**80-20 Split:** This split achieves the highest accuracy at 90%, but
the recall for fraudulent transactions is only 0.69, which could lead to
more false negatives. While useful for overall accuracy, it may not be
the best choice for fraud detection.

6.  50-50 split:

|              | Precision | recall | F1-score | support |
|--------------|-----------|--------|----------|---------|
| 0            | 0.88      | 0.88   | 0.88     | 1000    |
| 1            | 0.88      | 0.88   | 0.88     | 10000   |
| accuracy     |           |        | 0.88     | 2000    |
| Marco avg    | 0.88      | 0.88   | 0.88     | 2000    |
| Weighted avg | 0.88      | 0.88   | 0.88     | 2000    |

**50-50 Split:** With an accuracy of 88%, this split provides equal
representation of both classes in training and testing. However, it does
not offer a clear advantage over 70-30 and may reduce training
efficiency due to a smaller training set.

## **Conclusion**

Based on the classification reports for various train-test splits
analyzed, the **70-30 split demonstrates the best overall performance**.
It maintains a strong balance between precision, recall, and F1-score
for both classes while ensuring sufficient data for both training and
evaluation.

While the **80-20 split** shows slightly higher accuracy, the recall for
the fraudulent class (1) is lower, which may reduce the model\'s ability
to detect fraudulent transactions effectively. The **55-45 and 50-50
splits** also perform well but do not provide a significant advantage
over the 70-30 split.

Considering these results, the **70-30 split is the most suitable
choice**, offering a reliable trade-off between training efficiency and
model evaluation. Moving forward, we will proceed with this split for
further model development and testing on the full dataset.
