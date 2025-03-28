Literature Review

<table>
<tbody>
<tr class="odd">
<td>Sl.No</td>
<td>Title</td>
<td>Link</td>
<td>Published Date</td>
<td>Description</td>
</tr>
<tr class="even">
<td>1</td>
<td><p>X-SHAoLIM: Novel Feature Selection Framework for Credit Card
Fraud Detection</p>
<p><em>(transactionAmt,TransactionRatio_E7,HourlyTransactionCount_E13)</em></p></td>
<td><a
href="https://jad.shahroodut.ac.ir/article_3076_3e6666971ffb1d5e06497b685d813741.pdf?utm_source=chatgpt.com">Link</a></td>
<td>January 2024</td>
<td><p>X-SHAoLIM is an ensemble-based explainable feature selection
framework for credit card fraud detection using SHAP and LIME. It
identifies the top 50 features—such as transaction amount, spending
patterns, and behavioral attributes—to balance accuracy,
interpretability, and efficiency. The selection process involves SHAP
ranking, voting, and LIME filtering to remove irrelevant features,
reducing overfitting and computational costs while enhancing fraud
detection performance.</p>
<p>Research Gap:Your project enhances X-SHAoLIM by offering broader
model selection, adaptive feature optimization (Optuna), improved
resampling (SMOTE), and fine-tuned models (GridSearchCV,
RandomizedSearchCV). Unlike the study’s fixed feature selection and
undersampling, your approach is more dynamic and robust. Additionally,
your project prioritizes real-time scalability for practical fraud
detection in payment systems.</p></td>
</tr>
<tr class="odd">
<td>2</td>
<td><p>A machine learning based credit card fraud</p>
<p>detection using the GA algorithm for feature</p>
<p>selection</p>
<p><br />
(transactionAmt,Transaction_E4)</p></td>
<td><a
href="https://journalofbigdata.springeropen.com/articles/10.1186/s40537-022-00573-8">Link</a></td>
<td>February 2022</td>
<td><p>The study uses a Genetic Algorithm (GA) with Random Forest (RF)
as the fitness function to optimize feature selection for credit card
fraud detection. It selects key features, including transaction amount,
time, behavioral attributes (V1-V28), and risk indicators, reducing
dimensionality while improving accuracy. SMOTE is applied to handle
class imbalance, ensuring effective fraud detection. The GA-RF model
achieved 99.98% accuracy, demonstrating that feature selection enhances
performance while reducing overfitting and computational costs.</p>
<p>Research Gap:<strong><strong>Compared to the GA-based feature
selection approach, our project incorporates a wider range of models,
adaptive feature selection, hybrid resampling, hyperparameter tuning,
and real-time deployment strategies. These enhancements make your fraud
detection framework more scalable, optimized, and effective for
real-world payment security applications. </strong></strong></p></td>
</tr>
<tr class="even">
<td>3</td>
<td><p>Solving the “false positives” problem in fraud prediction</p>
<p>Automated Data Science at an Industrial Scale</p>
<p>(transactionAmoutVariance_E6,transactionVelocity_E10,AvgTransactionAmt_24hrs_E9)</p></td>
<td><a href="https://arxiv.org/pdf/1710.07709">Link</a></td>
<td>October 2017</td>
<td><p>The authors used the <strong><strong>Deep Feature Synthesis
(DFS)</strong></strong> algorithm to automatically generate
<strong><strong>237 features</strong></strong> for each transaction,
capturing over <strong><strong>100 behavioral patterns</strong></strong>
from historical data linked to each card. These features provided a more
detailed view of transaction behaviors. They then trained a
<strong><strong>random forest classifier</strong></strong> on these
engineered features, leveraging its robustness for fraud detection. The
model was tested on <strong><strong>1.852 million
transactions</strong></strong> from a multinational bank, reducing
<strong><strong>false positives by 54%</strong></strong> and saving
approximately <strong><strong>190,000 euros</strong></strong> compared
to the bank’s existing system. For deployment, the study found that
<strong><strong>recalculating historical features
weekly</strong></strong> maintained similar performance, eliminating the
need for continuous real-time computation and optimizing resource
use.</p>
<p>Research Gap:The study is limited to a specific dataset, reducing
generalizability. Alternative feature engineering techniques and deep
learning methods remain unexplored. The impact of feature update
frequency on detection performance needs further analysis. While false
positives are reduced, improving recall without high computational costs
is an open challenge.</p></td>
</tr>
<tr class="odd">
<td>4</td>
<td><p>A fraud detection model based on feature selection</p>
<p>and undersampling applied to Web payment systems</p>
<p><a
href="https://www.researchgate.net/publication/304298963_A_Fraud_Detection_Model_Based_on_Feature_Selection_and_Undersampling_Applied_to_Web_Payment_Systems"></a></p>
<p>(transactionAmt,transactionDT,isFraud)</p></td>
<td><a
href="http://Detection_Model_Based_on_Feature_Selection_and_Undersampling_Applied_to_Web_Payment_Systems/">Link</a></td>
<td>December 2015</td>
<td><p>The study focused on improving fraud detection in web
transactions by selecting the most predictive features and addressing
class imbalance through undersampling. The selection of top features
helped reduce data dimensionality by eliminating noise and irrelevant
attributes, making the model more efficient. It also mitigated
overfitting, ensuring the classifier learned meaningful fraud patterns
rather than memorizing noise. </p>
<p>Research Gap:Compared to our project, which leverages
<strong><strong>advanced ML models (LightGBM, CatBoost,
XGBoost)</strong></strong>, <strong><strong>SMOTE
resampling</strong></strong>, and <strong><strong>hyperparameter tuning
(Optuna, GridSearchCV, RandomizedSearchCV)</strong></strong>, the study
has several gaps. It relies on <strong><strong>basic
classifiers</strong></strong>, <strong><strong>manual feature
selection</strong></strong> instead of adaptive optimization, and
<strong><strong>undersampling</strong></strong>, which may cause data
loss. Additionally, it lacks <strong><strong>hyperparameter
tuning</strong></strong> and <strong><strong>real-world
deployment</strong></strong>, making it less scalable. Our project
improves fraud detection by focusing on <strong><strong>better feature
selection, model tuning, and real-time applicability</strong></strong>,
making it more effective for payment security.</p></td>
</tr>
<tr class="even">
<td>5</td>
<td>E-Commerce Fraud Detection Based on Machine Learning Techniques:
Systematic Literature Review</td>
<td><a
href="https://ieeexplore.ieee.org/document/10506811">Link</a></td>
<td>June 2024</td>
<td></td>
</tr>
<tr class="odd">
<td>6</td>
<td><p>Real-Time Fraud Detection Using Machine Learning</p>
<p> (transactionRatio_E7,transaction_E11)</p></td>
<td><a
href="https://www.scirp.org/pdf/jdaip2024122_42870691.pdf">Link</a></td>
<td>May 2024</td>
<td><p>The paper focuses on <strong><strong>real-time credit card fraud
detection</strong></strong> using
<strong><strong>SMOTE</strong></strong> to handle data imbalance and
compares multiple ML models, including <strong><strong>Random Forest,
XGBoost, and LightGBM</strong></strong>. <strong><strong>Random Forest
performed best</strong></strong>, achieving high accuracy and recall.
<strong><strong>SHAP values</strong></strong> were used for feature
explainability, identifying <strong><strong>V12 and
V14</strong></strong> as key fraud indicators. Evaluation metrics
include <strong><strong>AUC, PRAUC, F1-score, KS, recall, and
precision</strong></strong>.</p>
<p>Research Gap:The paper lacks <strong><strong>real-time API
deployment</strong></strong>, does not address <strong><strong>adapting
to new fraud patterns (concept drift)</strong></strong>, and
<strong><strong>misses hyperparameter tuning with
Optuna</strong></strong>. While it uses
<strong><strong>SMOTE</strong></strong>, it does not explore
<strong><strong>synthetic fraud data generation</strong></strong> or
<strong><strong>model adaptability to new device
types</strong></strong>.</p></td>
</tr>
<tr class="even">
<td>7</td>
<td><p>Fraud Detection Using Optimized Machine Learning Tools Under
Imbalanced Classes</p>
<p>(SMOTE,Hyperparameter Tuning)</p></td>
<td><a href="https://arxiv.org/abs/2209.01642">Link</a></td>
<td>September 2022</td>
<td><p>The research compares four fraud detection models—Logistic
Regression, Decision Trees, Random Forest, and XGBoost—using real-world
phishing website and credit card fraud datasets. To address data
imbalance, they apply RUS, SMOTE, and SMOTEENN techniques. Models are
fine-tuned with RandomizedSearchCV and evaluated using AUC ROC and AUC
PR. XGBoost performs best overall, while Random Forest with SMOTE
achieves high accuracy for credit card fraud. RUS increases false
alarms, making it impractical.</p>
<p><strong><strong>Research Gap:</strong></strong>The study does not
explore neural networks, lacks deeper fine-tuning, and fails to explain
SMOTEENN's poor performance. It also does not investigate optimal
feature selection, dataset generalizability, or model adaptation to
evolving fraud patterns.</p></td>
</tr>
<tr class="odd">
<td></td>
<td><p>(transactionVelocity_E10,transactionVariance_E6)</p></td>
<td><a href="https://arxiv.org/pdf/2406.04658v1">Link</a></td>
<td>June 2024</td>
<td><p>The paper improves online payment fraud detection using SMOTE for
data balancing, XGBoost and LightGBM for high accuracy, and an ensemble
model with a neural network for enhanced performance. It fine-tunes
hyperparameters and removes noise, achieving superior fraud detection
results.</p>
<p><strong><strong>Research Gap:</strong></strong>The study relies only
on SMOTE, lacks feature engineering, and does not include real-time
detection via an API. It also does not address how the model adapts to
new fraud patterns and devices without retraining.</p></td>
</tr>
<tr class="even">
<td>9</td>
<td><p>On the Potential of Network-Based Features for Fraud
Detection</p>
<p>(transaction_E4,transaction_E2,HourWiththinSlot_E3)</p></td>
<td><a href="https://arxiv.org/pdf/2402.09495">Link</a></td>
<td>February 2024 </td>
<td><p>The <strong><strong>"Day of Week"</strong></strong> and
<strong><strong>"Time of Day"</strong></strong> features were created to
capture temporal behavioral patterns in transaction data, helping detect
deviations that may indicate fraud. In the paper, the
<strong><strong>Day of Week</strong></strong> feature was engineered by
analyzing the historical transaction behavior of each user and comparing
the current transaction's day to their usual transaction days. If a
transaction occurs on a day when the user rarely transacts, it raises a
suspicion score. Similarly, the <strong><strong>Time of
Day</strong></strong> feature was developed by computing the average
transaction times for each customer over a defined historical period
(e.g., the past seven days) and comparing it to the transaction time of
the current event. This allows the model to detect anomalies, such as
transactions occurring at odd hours when the customer typically does not
make purchases. The authors validated the significance of these features
by integrating them into a logistic regression model and measuring their
impact on fraud detection performance. The feature importance analysis
revealed that <strong><strong>Time of Day</strong></strong> had a
notable contribution, with a moderate importance score, while
<strong><strong>Day of Week</strong></strong> also provided useful
insights into fraudulent behavior patterns. These features were critical
in identifying unusual transaction timings, which fraudsters often
exploit to bypass detection systems.</p>
<p>Research Gap:The study enhances fraud detection using the PPR
exposure score with traditional features, but gaps remain. It is tested
on a specific dataset, limiting generalizability. Alternative
graph-based methods like GNNs are unexplored, and the impact of
real-time feature updates on model adaptability is not assessed.
Additionally, balancing computational efficiency with detection accuracy
in large-scale transactions requires further research.</p></td>
</tr>
<tr class="odd">
<td>10</td>
<td><p>Fraud Detection Using Random Forest, Neural Autoencoder, and
Isolation Forest</p>
<p>(transactionAmt,transactionDT)</p></td>
<td><a
href="https://www.infoq.com/articles/fraud-detection-random-forest/">Link</a></td>
<td>August 2019</td>
<td>The project uses supervised and unsupervised ML techniques for
credit card fraud detection, with Random Forest as the primary model. It
balances data using stratified sampling, fine-tunes decision thresholds,
and applies Autoencoder Neural Networks and Isolation Forest for anomaly
detection. The Kaggle credit card fraud dataset is used, with PCA for
feature extraction.</td>
</tr>
</tbody>
</table>
