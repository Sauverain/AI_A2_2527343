# Personal Interpretation of AI Model Results

**Student:** Alain Sauverain ISHEMA  
**Registration Number:** 25/27343  
**Email:** ug2527343@ines.ac.rw  
**Verification Code:** AI-A2-7343  
**Course:** SWE 3513 – Artificial Intelligence

## 1. Regression Interpretation

In row 2, the actual harvest was 12.9863 tons, while the model predicted 10.7003 tons. This gives an error of -2.2860 tons. The negative value means that the model predicted a smaller harvest than the actual harvest.

This error is important because farmers and cooperatives in Musanze may use harvest predictions to plan transport, storage and sales. If the prediction is too low, they might not prepare enough transport or storage space.

To understand this error better, I would check the rainfall, temperature and field size measurements. These values can affect harvest predictions. I would also compare the prediction with actual farm records before using it for important decisions.

## 2. Classification Interpretation

In row 28, the actual risk class was 1, but the model predicted 0, with a high-risk probability of 0.4500. This is called a false negative because the model failed to identify a farm that was actually high risk.

This mistake could be serious because an agricultural officer might think the farm is safe and fail to provide support on time.

For this reason, I think AI predictions should support human decisions instead of replacing them. Agricultural officers should review uncertain predictions and check the farm's actual condition before making a final decision.

## 3. Clustering Interpretation

Cluster 0 contains 86 farms with similar characteristics. Their average rainfall was 1017.9 mm, average temperature was 19.7°C and average field size was 2.01 hectares. All farms in this training group had cooperative support.

This information could help agricultural cooperatives plan field visits and training activities. For example, officers could organize group training sessions for farmers with similar conditions instead of visiting each farm separately.

However, being in the same cluster does not mean that the farms have the same level of risk. Clustering only shows similarities between the farm records. Each farm still needs individual assessment when necessary.

## 4. Personal Reflection

This project shows how artificial intelligence can support agricultural planning. Regression helps estimate harvest quantities, classification helps identify possible risks, and clustering helps group farms with similar characteristics.

One important lesson from the results is that AI models can make mistakes. For example, the regression model underestimated one harvest, and the classification model failed to identify one high-risk farm. This means AI predictions should be checked before they are used for important agricultural decisions.

One improvement I would recommend is adding a review process for farms with uncertain risk predictions. This would allow agricultural officers to examine those farms more carefully instead of relying only on the model.

I also understand that the project uses synthetic data. Therefore, the results are suitable for learning and demonstrating machine learning, but the system would need further testing with real agricultural data before practical use.