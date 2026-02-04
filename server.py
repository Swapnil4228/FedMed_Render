import flwr as fl
import torch
from model import ChestNet
from flwr.common import parameters_to_ndarrays

model = ChestNet()

class SaveStrategy(fl.server.strategy.FedAvg):

    def aggregate_fit(self, server_round, results, failures):
        aggregated = super().aggregate_fit(server_round, results, failures)

        if aggregated is not None:
            params, _ = aggregated
            self.save_global_model(params)

        return aggregated

    def save_global_model(self, parameters):
        ndarrays = parameters_to_ndarrays(parameters)

        state_dict = dict(zip(
            model.state_dict().keys(),
            [torch.tensor(nd) for nd in ndarrays]
        ))

        torch.save(state_dict, "global_model.pth")
        print("\n✅ Global model saved as global_model.pth\n")

def main():
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=3),
        strategy=SaveStrategy()
    )

if __name__ == "__main__":
    main()
