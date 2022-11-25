""" Describes Config, a simple namespace for config values.

For description of all config values, refer to config.toml.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Config:  # pylint: disable=too-many-instance-attributes, too-few-public-methods
    """ Contains values needed to set up the coreference model. """
    section: str

    data_dir: str

    train_data: str
    dev_data: str
    test_data: str

    device: str

    bert_model: str
    bert_window_size: int

    embedding_size: int
    sp_embedding_size: int
    a_scoring_batch_size: int
    hidden_size: int
    n_hidden_layers: int

    max_span_len: int

    rough_k: int

    bert_finetune: bool
    dropout_rate: float
    learning_rate: float
    bert_learning_rate: float
    train_epochs: int
    bce_loss_weight: float

    tokenizer_kwargs: Dict[str, dict]
    conll_log_dir: str
    
    genre: str
    with_speaker: bool

    def __str__(self):
        return "train_data: " + self.train_data + "\ndev_data: " + self.dev_data + "\ntest_data: " + self.test_data + "\ndevice: " + self.device + "\nbert_model: " + self.bert_model + "\nbert_window_size: " + str(self.bert_window_size) + "\nembedding_size: " + str(self.embedding_size) + "\nsp_embedding_size: " + str(self.sp_embedding_size) + "\na_scoring_batch_size: " + str(self.a_scoring_batch_size) + "\nhidden_size: " + str(self.hidden_size) + "\nn_hidden_layers: " + str(self.n_hidden_layers) + "\nmax_span_len: " + str(self.max_span_len) + "\nrough_k: " + str(self.rough_k) + "\nbert_finetune: " + str(self.bert_finetune) + "\ndropout_rate: " + str(self.dropout_rate) + "\nbert_learning_rate: " + str(self.bert_learning_rate) + "\nlearning_rate: " + str(self.learning_rate) + "\ntrain_epochs: " + str(self.train_epochs) + "\nbce_loss_weight: " + str(self.bce_loss_weight) + "\nconll_log_dir: " + self.conll_log_dir + "\ngenre: " + self.genre + "\nwith_speaker: " + str(self.with_speaker)


        