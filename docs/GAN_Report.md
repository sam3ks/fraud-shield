Generative Adversarial Networks (GAN)

GAN is a type of machine learning model that can create new data that
looks very similar to real data.

The GAN architecture consists of two neural networks:

- ****Generator****:

  - Creates synthetic (fake) data from random noise.

    Its goal is to produce data that looks as real as possible.

- **Discriminator**:

  - Evaluates whether given data is real or fake.

    Outputs a probability score indicating authenticity.

The two networks Generator and Discriminator work together to create the
dataset :

- The generator tries to fool the discriminator by making increasingly
  realistic fake data.

<!-- -->

- The discriminator tries to accurately detect fake data.

<!-- -->

- Both start with random weights, meaning they initially do not know
  anything about the data.

The generator takes the random noise and transforms it through multiple
layers into synthetic data. Its goal is to produce data that resembles
the real data as closely as possible. The discriminator's job is to
distinguish between real data (from the dataset) and fake data (from the
generator). It outputs a probability score that indicates whether the
input is real or fake.

This happens in alternating cycles:

- - The discriminator learns from both real and generated data.
  - The generator updates its weights based on how well it can trick the
    discriminator.

Both networks update their parameters using backpropagation and
optimization techniques like Adam optimizer.

Vanilla GAN

Vanilla GAN is the ****simplest and original form**** of GAN.

Consists of two fully connected neural networks:

- **Generator**: Takes random noise and outputs continuous, real-like
  data.
- **Discriminator**: Judges whether data is real or generated.

It uses simple loss functions (Binary Cross Entropy) and focuses on
****continuous numeric data****.

Vanilla GAN can be used in:

- ****Image data generation**** (simple, grayscale datasets like MNIST).
- ****Basic continuous numeric data**** generation where all values are
  floating-point and there's no categorical or discrete data.
- ****Proof-of-concept projects**** or understanding GAN fundamentals.

Why the Vanilla GAN cannot be used in generating dataset for Fraud
Detection:

- Fraud detection datasets have engineered features, conditions, and
  anomaly indicators. Vanilla GAN lacks conditional handling.
- ****Cannot handle categorical or binary outputs natively**** , it will
  generate continuous floating-point numbers, requiring manual
  post-processing (like rounding or mapping).
- ****Ignores minority classes in highly imbalanced columns**** , in
  fraud detection datasets, fraud cases are rare. Vanilla GAN tends to
  suffer from *mode collapse*, ignoring minority classes and generating
  only majority class examples.

Conditional GAN

****A Conditional GAN is an extension of the Vanilla GAN where both the
generator and discriminator receive additional information (conditions)
alongside their inputs.****

- These conditions can be ****class labels****, ****attributes****, or
  ****any feature**** that you want to control.
- By providing these conditions, the generator learns to produce data
  corresponding to a specific category or condition, and the
  discriminator learns to verify if the sample matches the given
  condition.
- ****Generator Input: Random noise + condition vector (label or other
  feature)****
- ****Discriminator Input:**** Data sample ****+ condition vector****

<!-- -->

- The generator tries to generate data that fits the given condition.
  The discriminator tries to detect if the generated data matches both
  realism ****and**** the given condition.

****

**Advantages of Using Conditional GAN:**

- ****Better control****: Conditional GANs let you generate data for
  specific classes, allowing focused creation of rare or important
  categories like fraud cases.
- ****More diversity****: Conditioning prevents repetition and ensures
  the generator creates varied and realistic samples across categories.
- ****Helps with imbalance****: You can easily generate more samples for
  underrepresented classes, making the dataset more balanced and
  improving model performance.

Conditional GAN can be used in:

- Image generation conditioned on labels (e.g., generate images of a
  specific digit or object)
- Data augmentation for ****imbalanced classification datasets****
- Fraud detection datasets to generate samples for the rare \"fraud\"
  class

Why the Conditional GAN cannot be used in generating dataset for Fraud
Detection:

- Struggles to learn complex relationships between columns.
- Works better with simple conditions, not mixed numerical and
  categorical data.
- Has difficulty handling extremely imbalanced classes.
- Outputs continuous values for categorical columns, requiring extra
  post-processing.

Table GAN

****TableGAN**** is a specialized type of GAN specifically designed for
****generating synthetic tabular data**** , datasets consisting of rows
and columns with both continuous and categorical features.

It's an advancement over Vanilla GAN because:

- It is built to ****handle structured, tabular data**** rather than
  images or unstructured data.
- It doesn't just learn to generate \"realistic\" samples; it tries to
  ****learn the distributions of multiple features together**** in a
  row.

The **Generator (G)** takes a random noise vector as input and generates
a complete row of synthetic tabular data that imitates the patterns,
distributions, and relationships found in the original dataset.

The **Discriminator (D)** receives a row of data (which can be either
real or generated) and evaluates whether it is real or fake by comparing
it to the true data distribution and verifying if the relationships
between columns are realistic.

Unlike typical GANs that generate a single output like an image or one
item, here the generator is designed to produce an entire row of tabular
data in one go.

**Advantages** **of Using Table** **GAN:**

- ****Can handle multiple feature types (after encoding):**** It works
  with both numerical and categorical features, although categorical
  features need proper encoding before training.
- ****Captures feature-to-feature correlations:**** It effectively
  learns and preserves relationships between columns --- crucial for
  datasets like fraud detection, where features such as region, card
  number, and merchant email interact.
- ****Generates full rows in one shot:**** The generator produces
  complete synthetic records at once, making it easy and efficient to
  create entire synthetic datasets.

Table GAN can be used in:

- Privacy-preserving data generation for sensitive tabular datasets
  (e.g., healthcare, banking)
- Data augmentation for tabular datasets with class imbalance (e.g.,
  fraud detection, credit risk)
- Generating large synthetic datasets for testing databases, analytics
  pipelines, and simulation studies

Why the Table GAN cannot be used in generating dataset for Fraud
Detection:

- Focuses on replicating overall distribution, not generating samples
  for rare fraud cases.

- Struggles to capture complex conditional relationships between
  features.

- Produces invalid categorical/binary values, requiring heavy
  post-processing.

Copula GAN

CopulaGAN is an advanced type of GAN that combines:

- **Generative Adversarial Networks (GANs)** for synthetic data
  generation.
- **Copulas** to model complex dependencies between columns, especially
  for mixed data types (numerical + categorical).
- ****Copula-based Transformation:**** Converts each feature into a
  uniform distribution (0 to 1), making both continuous and categorical
  features easier to model.

<!-- -->

- **GAN Training in Copula Space:** The generator and discriminator are
  trained on this normalized data, learning feature dependencies and
  patterns.

<!-- -->

- **Inverse Transformation:** The generated data is mapped back from
  copula space to the original scale and categories, producing realistic
  synthetic data.

**Advantages** **of Using Copula** **GAN:**

- It handles both numerical and categorical data types effectively.

<!-- -->

- It captures complex dependencies between columns better than simpler
  GAN models.

<!-- -->

- It reduces mode collapse, ensuring minority patterns are not ignored.

<!-- -->

- It works well for datasets where relationships between columns are
  highly non-linear.

Copula GAN can be used in:

-  Generating synthetic healthcare records while preserving statistical
  dependencies.

-  Creating financial transaction datasets that model realistic
  correlations.

-  Privacy-preserving data generation for sensitive datasets (banking,
  HR).

-  Data augmentation in domains where maintaining feature relationships
  is crucial

Why the Copula GAN cannot be used in generating dataset for Fraud
Detection:

- It does not provide direct conditional control to generate specific
  classes.
- It struggles to handle extreme class imbalance, producing fewer rare
  cases.
- It may fail to capture subtle and complex fraud patterns between
  features.

**CTGAN ( Conditional Tabular Generative Adversarial Networks):**

**CTGAN**, part of the SDV (Synthetic Data Vault) library, is a
specialized GAN model designed to generate realistic tabular synthetic
data while preserving complex relationships between numerical and
categorical columns.

****How CTGAN works:****

- **Conditional vector:**  
  At each step, a random category is chosen, and the generator is
  conditioned on that category. This makes CTGAN ideal for handling
  imbalanced datasets and generating more samples for rare classes.

- **Generator (G):**  
  Takes random noise and conditional input, outputting synthetic tabular
  data rows.

- **Discriminator (D):**  
  Determines if the input row (real or synthetic) matches the true data
  distribution and checks whether the conditional rule was followed.

### Why it is preferred over Vanilla GAN, TableGAN, and CopulaGAN:

- Introduces ****conditional generation****, allowing the model to focus
  on generating data for specific rare categories (like fraud).

- Handles ****skewed continuous distributions**** with mode-specific
  normalization.

- Learns complex relationships between categorical and numerical columns
  effectivel

CTGAN can be used in:

-  Data augmentation for underrepresented categories
-  Privacy-preserving tabular data creation (finance, healthcare)
-  Testing machine learning models and pipelines with large synthetic
  data

Steps to Use CTGAN

**1. Loading the Original Dataset**

Begin by loading original transactional dataset into a pandas DataFrame:

import pandas as pd

file_path = \"/content/bengaluru_fraud_data.csv\"

df = pd.read_csv(file_path)

### ****2. Detecting Metadata**** {#detecting-metadata}

CTGAN requires metadata to understand the dataset's structure.  
You can automatically detect this using SingleTableMetadata

from sdv.metadata import SingleTableMetadata

metadata = SingleTableMetadata()

metadata.detect_from_dataframe(df)

The metadata detection process identifies:

- Column types (categorical, numerical, datetime)
- Distributions of each column
- Relationships and dependencies between columns

3\. Training the CTGAN Model

Use CTGANSynthesizer to train the model on data:

from sdv.single_table import CTGANSynthesizer

model = CTGANSynthesizer(metadata, epochs=50, batch_size=500)

model.fit(df)

- The epochs and batch_size parameters can be adjusted based on dataset
  size and complexity.

<!-- -->

- More epochs allow deeper learning but may increase computation time.

<!-- -->

- A larger batch size can stabilize training for bigger datasets.

### ****4. What CTGAN Learns**** {#what-ctgan-learns}

During training, CTGAN captures:

- **Numerical patterns** (e.g., transaction amounts, time intervals)
- **Categorical distributions** (e.g., fraud labels, product codes)
- **Column dependencies** (e.g., certain card types associated with
  specific transaction patterns)

### ****5. Generating Synthetic Data**** {#generating-synthetic-data}

Once training is complete, generate synthetic data based on the learned
patterns:

\# Generate synthetic data (10x the original dataset size)

n_samples = len(df) \* 10

synthetic_data = model.sample(n_samples)

### ****6. Saving the Generated Data**** {#saving-the-generated-data}

Finally, save the synthetic dataset for further analysis or modeling:

\# Save the generated dataset

synthetic_data.to_csv(\"synthetic_data_ctgan.csv\", index=False)

print(\"Synthetic dataset generated and saved as
\'synthetic_data_ctgan.csv\'\")

### Rule-of-Thumb Approach for Data Size in Machine Learning

The **rule-of-thumb approach** is often used with smaller datasets. This
approach involves estimating the amount of data needed based on past
experiences and current knowledge.

- **Rule**: You need at least **ten times as many data points** as there
  are features in your dataset.
- Example: If your dataset has **10 columns (features)**, you should
  have at least **100 rows**.

#### Benefits of the Rule-of-Thumb Approach:

1.  Ensures enough high-quality input data is available.
2.  Helps avoid **data sample bias** and **underfitting** during the
    post-deployment phase.
3.  Speeds up the process of achieving predictive capabilities.

This approach provides a quick and efficient way to ensure that the data
you have is adequate for building a reliable machine learning model.

In **our dataset**, which has **47 columns**, the beginning dataset size
of **500 rows** is a good starting point. As we scale up, we will move
to **1000** and **2000 rows.**

Sources:

[*https://graphite-note.com/how-much-data-is-needed-for-machine-learning#:\~:text=Generally%20speaking%2C%20the%20rule%20of,100%20rows%20for%20optimal%20results*](https://graphite-note.com/how-much-data-is-needed-for-machine-learning#:~:text=Generally%20speaking%2C%20the%20rule%20of,100%20rows%20for%20optimal%20results)

[*https://cloud.google.com/vertex-ai/docs/tabular-data/bp-tabular*](https://cloud.google.com/vertex-ai/docs/tabular-data/bp-tabular)

****Comparison of Feature Distributions: Original vs GAN-Generated
Dataset****

![](Pictures/1000000000000320000001B155D35E69E9BD8A60.jpg){width="17cm"
height="9.2cm"}

*Name: TransactionAmt, dtype: float64*

*KS Test for TransactionAmt: Statistic=0.2360, p-value=0.0000*

*Distributions of TransactionAmt are significantly different (p \<
0.05).*

![](Pictures/1000000000000320000001B1F5881CF1D6A187EE.jpg){width="17cm"
height="9.2cm"}

*Name: Distance, dtype: float64*

*KS Test for Distance: Statistic=0.4090, p-value=0.0000*

*Distributions of Distance are significantly different (p \< 0.05).*

![](Pictures/1000000000000320000001AF3514A3A3563377A8.jpg){width="17cm"
height="9.158cm"}

*Chi-Square Test for ProductCD: Statistic=2.0514, p-value=0.8420*

*Distributions of ProductCD are similar (p \>= 0.05).*

![](Pictures/1000000000000320000001C1FD85FE5844D6B7C3.jpg){width="17cm"
height="9.541cm"}

*Chi-Square Test for CardNetwork: Statistic=4.7351, p-value=0.1923*

*Distributions of CardNetwork are similar (p \>= 0.05).*

![](Pictures/10000000000003200000019B95562AD7437BA49B.jpg){width="17cm"
height="8.733cm"}

*Chi-Square Test for DeviceType: Statistic=0.0057, p-value=0.9396*

*Distributions of DeviceType are similar (p \>= 0.05).*

![](Pictures/1000000000000320000001AE89E6E5A8868BAD22.jpg){width="17cm"
height="9.137cm"}

*Chi-Square Test for User_Region: Statistic=6.2712, p-value=0.9849*

*Distributions of User_Region are similar (p \>= 0.05).*

![](Pictures/1000000000000320000001C10737EF8BA9E0E8BD.jpg){width="17cm"
height="9.541cm"}

*Chi-Square Test for Order_Region: Statistic=7.4557, p-value=0.9999*

*Distributions of Order_Region are similar (p \>= 0.05).*

![](Pictures/1000000000000320000001C090664832D1E8C765.jpg){width="17cm"
height="9.52cm"}

*Chi-Square Test for Receiver_Region: Statistic=16.0788, p-value=0.9646*

*Distributions of Receiver_Region are similar (p \>= 0.05).*

![](Pictures/1000000000000320000001BB8322DEED2EED292C.jpg){width="17cm"
height="9.414cm"}

*KS Test for Transaction Hour: Statistic=0.1480, p-value=0.0012*

*Distributions of Transaction Hour are significantly different (p \<
0.05).*
