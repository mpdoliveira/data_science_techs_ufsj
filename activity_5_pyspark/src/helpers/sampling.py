from helpers.helper import start_df

df = start_df()

sample_df = df.sample(withReplacement=False, fraction=0.05, seed=42)

sample_df.write.csv("amostra.csv", header=True, encoding="utf-8")
