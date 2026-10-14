from helper import start_df

df = start_df()

sample_df = df.sample(withReplacement=False, fraction=0.1, seed=42)

sample_df.write.csv("amostra_10.csv", header=True, encoding="utf-8")
