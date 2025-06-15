

|  | Model 1 Default2 Hidden 32-16 | Model 23 Hidden64-32-16 with engram  | Model 34 Hidden 128-64 \-32-16 with engram  |
| :---- | :---- | :---- | :---- |
| Number of Parameters | (19500x32)+32+(32x16)+16+(16x18)+18=624032+528+306=624926 | (19500x64)+64+(64x32)+32+(32x16)+16+(16x18)+18=1250978 | (19500x128)+128+(128x64)+64+(64x32)+32+(32x16)+16+(16x18)+18=2507298 |
| Precision | 0.5 | 0.37 | 0.38 |
| Recall | 0.3 | 0.35 | 0.38 |
| F1-score | 0.29 | 0.35 | 0.38 |
| Time | 1 min 49 sec | 2 min 47 sec | 3 min 31 sec |

Figure 1.1 Performance comparison of different Neural Network Design 

## Methods and Results

The combined data was pre-processed by standardizing column headers, removing superfluous text and duplicate entries, and handling missing values. In the code corrected typographical errors in state/region names using fuzzy-string matching against a reference list of official spellings, applying a 90% similarity threshold.

Initially, the code converted over 15,000 unique place names into features using one-hot encoding. This approach created a high-dimensional sparse matrix (\~19,500 features) but failed to capture linguistic patterns, preventing the model from generalizing to new names.  
To address this, I implemented an n-gram character model. This technique reduced feature dimensionality to a compact set of 1,000 informative sequences, significantly decreasing memory use and training time. Across models, early stopping (patience=10) reduced computation time by at least four minutes.

## Discussion and Conclusion

Figure1 states that ,Increasing model complexity by adding hidden layers did not yield significant performance improvements. The disparity between high training accuracy and lower testing accuracy suggested overfitting.

I conclude that the primary performance bottleneck is not model complexity but data quality. Many Myanmar villages share identical or near-identical names across different regions, creating inherent label ambiguity. Since the n-gram features for these names are the same, even a more complex model cannot distinguish their correct regions and instead overfits to the training data's patterns. The limiting factor is the quality and ambiguity of the source data rather than the model's architecture.

