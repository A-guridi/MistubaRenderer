from src.main.Module import Module
from src.utility.PostProcessingUtility import PostProcessingUtility

class TrimRedundantChannels(Module):
    """ Removes redundant channels, where the input has more than one channels that share exactly the same value """
    def __init__(self, config):
        Module.__init__(self, config)

    def run(self, image, key, version):
        """
        :param image: The image data.
        :return: The trimmed image data.
        """
        return PostProcessingUtility.trim_redundant_channels(image), key, version
