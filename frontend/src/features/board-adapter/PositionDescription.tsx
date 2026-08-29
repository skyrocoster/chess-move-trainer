import { Disclosure } from "../design-system/Disclosure";
import styles from "./PositionDescription.module.css";
import { castlingNotation, orientationLabel, sideLabel } from "./positionDescriptionModel";
import type { PositionModel } from "./positionDescriptionModel";

export type { BoardOrientation, PositionModel } from "./positionDescriptionModel";

function VisiblePositionSummary({ model }: { model: PositionModel }) {
  return (
    <div className={styles.descriptionDisclosure} aria-hidden="true" inert>
      <div className={styles.positionSummary} data-position-summary>
        <div className={styles.positionMetadata} data-position-metadata>
          <div className={styles.metadataItem} data-position-metadata-item="orientation">
            <span className={styles.metadataLabel}>Orientation</span>
            <span className={styles.metadataValue}>{orientationLabel(model.orientation)}</span>
          </div>
          <div className={styles.metadataItem} data-position-metadata-item="side-to-move">
            <span className={styles.metadataLabel}>Side to move</span>
            <span className={styles.metadataValue}>{sideLabel(model.sideToMove)}</span>
          </div>
        </div>
        <div className={styles.positionInventories} data-position-inventories>
          {model.inventories.map((inventory) => (
            <section
              className={styles.sideInventory}
              key={inventory.color}
              data-position-side={inventory.color}
              data-position-side-to-move={model.sideToMove === inventory.color}
            >
              <div className={styles.sideHeader}>
                <h3>{sideLabel(inventory.color)}</h3>
              </div>
              <div className={styles.pieceRows}>
                {inventory.groups.map((group) => (
                  <div
                    className={styles.pieceRow}
                    key={group.pieceType}
                    data-position-piece={group.pieceType}
                  >
                    <span className={styles.pieceLabel}>{group.label}</span>
                    <span className={styles.positionSquares} data-position-squares>
                      {group.squares.map((square) => (
                        <span
                          className={styles.squareToken}
                          key={square}
                          data-position-square={square}
                        >
                          {square}
                        </span>
                      ))}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>
        <div className={styles.positionFacts} data-position-facts>
          <span className={styles.factChip} data-position-fact="castling-white">
            Castling · White <strong>{castlingNotation(model.castlingRights.white)}</strong>
          </span>
          <span className={styles.factChip} data-position-fact="castling-black">
            Castling · Black <strong>{castlingNotation(model.castlingRights.black)}</strong>
          </span>
          <span className={styles.factChip} data-position-fact="en-passant">
            En-passant target <strong>{model.enPassantTarget}</strong>
          </span>
          <span className={styles.factChip} data-position-fact="halfmove">
            Halfmove clock <strong>{model.halfmoveClock}</strong>
          </span>
          <span className={styles.factChip} data-position-fact="fullmove">
            Fullmove <strong>{model.fullmoveNumber}</strong>
          </span>
        </div>
      </div>
    </div>
  );
}

export function PositionDescription({ model }: { model: PositionModel }) {
  return (
    <Disclosure className={styles.positionDescription} summary="Position description">
      <VisiblePositionSummary model={model} />
    </Disclosure>
  );
}
